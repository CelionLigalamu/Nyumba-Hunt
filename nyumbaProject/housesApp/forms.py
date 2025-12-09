from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text='Enter your full name or username',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[]
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators = []

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['phone_number']


class PaymentForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter M-Pesa phone number (e.g., 0722123456)',
            'pattern': '[0-9+\\-\\s]+',
            'title': 'Please enter a valid phone number'
        }),
        help_text='Format: 0722123456 or 254722123456'
    )
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Remove any non-digit characters except +
        phone_digits = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Validate length
        if len(phone_digits) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits")
        
        return phone