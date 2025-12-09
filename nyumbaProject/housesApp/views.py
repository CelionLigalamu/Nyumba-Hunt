from django.shortcuts import render, get_object_or_404,redirect # type: ignore
from django.contrib.auth import login, authenticate # type: ignore
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required # pyright: ignore[reportMissingModuleSource]
from django.contrib import messages # type: ignore
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import House, Booking, Payment
from .forms import BookingForm, UserRegistrationForm, PaymentForm
from .mpesa_service import mpesa_service
import json  

"""
shows a list of vacant houses
"""
def home(request):
    houses = House.objects.all().order_by('-id')
    context = {'houses': houses}
    return render(request, 'housesApp/home.html', context)

def house_detail(request, pk):
    house = get_object_or_404(House, pk=pk)
    context = {'house': house}
    return render(request, 'housesApp/houses_details.html', context)

"""
Allow a logged-in user to book a vacant house.
On successful booking, change house.status to 'occupied'.
 """
@login_required
def book_house(request, pk):
    house = get_object_or_404(House, pk=pk)
    if house.status != 'vacant':
     return redirect('housesApp:home')
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.house = house
            booking.save()
            house.status = 'occupied'
            house.save()
            messages.success(request, f'Successfully booked {house.title}!')
            return redirect('housesApp:dashboard')  
    else:
        form = BookingForm()

    context = {'house': house, 'form': form}
    return render(request, 'housesApp/book.html', context)


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in!')
            return redirect('housesApp:home')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'housesApp/login.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)  
        if form.is_valid():
            user = form.save()
            login(request, user) 
            messages.success(request, 'Account created and you are now logged in!')
            return redirect('housesApp:home')
        else:
            messages.error(request, 'Please correct the highlighted errors and try again.')
    else:
        form = UserRegistrationForm() 
    
    context = {'form': form} 
    return render(request, 'housesApp/register.html', context)


"""
 Show a landlord their houses and bookings.
"""
@login_required
def landlord_dashboard(request):
    houses_qs = House.objects.filter(owner=request.user).order_by('-id')

    stats = {
        'total': houses_qs.count(),
        'vacant': houses_qs.filter(status=House.STATUS_VACANT).count(),
        'occupied': houses_qs.filter(status=House.STATUS_OCCUPIED).count(),
    }

    context = {'houses': houses_qs, 'stats': stats}
    return render(request, 'housesApp/dashboard.html', context)


@login_required
def initiate_payment(request, booking_id):
    """Initiate M-Pesa STK Push payment for a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            phone_number = mpesa_service.format_phone_number(phone_number)
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.house.price,
                phone_number=phone_number,
                status=Payment.STATUS_PENDING
            )
            
            # Initiate STK Push
            result = mpesa_service.initiate_stk_push(
                phone_number=phone_number,
                amount=booking.house.price,
                house_id=booking.house.id,
                user_id=request.user.id
            )
            
            if result['status'] == 'success':
                payment.checkout_request_id = result.get('checkout_request_id')
                payment.save()
                messages.success(request, 'STK Push sent! Check your M-Pesa prompt')
                return redirect('housesApp:dashboard')
            else:
                payment.status = Payment.STATUS_FAILED
                payment.save()
                messages.error(request, f"Payment failed: {result.get('message', 'Unknown error')}")
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'booking': booking,
        'amount': booking.house.price
    }
    return render(request, 'housesApp/payment.html', context)


@csrf_exempt
@require_POST
def payment_callback(request):
    """M-Pesa payment callback endpoint"""
    try:
        data = json.loads(request.body)
        
        # Extract callback data
        result = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = result.get('CheckoutRequestID')
        result_code = result.get('ResultCode')
        result_desc = result.get('ResultDesc')
        
        # Find payment
        payment = Payment.objects.get(checkout_request_id=checkout_request_id)
        
        if result_code == 0:  # Success
            # Extract M-Pesa receipt
            callback_metadata = result.get('CallbackMetadata', {}).get('Item', [])
            mpesa_receipt = None
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    mpesa_receipt = item.get('Value')
                    break
            
            payment.status = Payment.STATUS_COMPLETED
            payment.mpesa_receipt_number = mpesa_receipt
            payment.save()
            
            # Mark booking as confirmed
            booking = payment.booking
            booking.save()
            
        else:  # Failed
            payment.status = Payment.STATUS_FAILED
            payment.save()
        
        # Return success response to Safaricom
        return JsonResponse({
            'ResultCode': 0,
            'ResultDesc': 'Received successfully'
        })
    
    except Payment.DoesNotExist:
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': 'Payment not found'
        }, status=404)
    except Exception as e:
        print(f"Callback error: {e}")
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': str(e)
        }, status=500)



