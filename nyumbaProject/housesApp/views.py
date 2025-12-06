from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import House, Booking
from .forms import BookingForm, UserRegistrationForm  

"""
shows a list of vacant houses
"""
def home(request):
    houses = House.objects.filter(status='vacant')  # only vacant houses
    context = {'houses': houses}
    return render(request, 'housesApp/home.html', context)

def house_detail(request, pk):
    house = get_object_or_404(House, pk=pk)
    context = {'house': house}
    return render(request, 'housesApp/house_detail.html', context)

"""
Allow a logged-in user to book a vacant house.
On successful booking, change house.status to 'occupied'.
 """
@login_required
def book_house(request, pk):
    house = get_object_or_404(House, pk=pk)
    if house.status != 'vacant':
     return redirect('houses:home')
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.house = house
            booking.save()
            house.status = 'occupied'
            house.save()
            return redirect('houses:dashboard')  
    else:
        form = BookingForm()

    context = {'house': house, 'form': form}
    return render(request, 'housesApp/book.html', context)

"""
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  
            return redirect('home') 
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'houses/login.html')
"""
def register_user(request):
   if request.method == 'POST':
        form = UserRegistrationForm(request.POST)  
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('home')
        else:
          form = UserRegistrationForm() 
    
          context = {'form': form} 
   return render(request, 'housesApp/register.html')


"""
 Show a landlord their houses and bookings.
"""
@login_required
def landlord_dashboard(request):
    owned_houses = House.objects.filter(owner=request.user)
    context = {'houses': owned_houses}
    return render(request, 'housesApp/dashboard.html', context)



