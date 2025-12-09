"""
M-Pesa Daraja STK Push Service
Handles all M-Pesa payment operations
"""
import json
import requests
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from .models import House
import base64


class MpesaService:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.business_short_code = settings.MPESA_BUSINESS_SHORT_CODE
        self.passkey = settings.MPESA_PASSKEY
        self.environment = settings.MPESA_ENVIRONMENT
        
        if self.environment == 'sandbox':
            self.auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            self.stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        else:
            self.auth_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            self.stk_push_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    
    def get_access_token(self):
        """Get access token from M-Pesa Daraja API"""
        try:
            response = requests.get(
                self.auth_url,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def initiate_stk_push(self, phone_number, amount, house_id, user_id, account_reference='NYUMBA_HUNT'):
        """
        Initiate STK Push for M-Pesa payment
        
        Args:
            phone_number: Customer's phone number (format: 254XXXXXXXXX)
            amount: Amount to charge
            house_id: ID of the house being booked
            user_id: ID of the user making payment
            account_reference: Reference for the transaction
        
        Returns:
            dict with transaction details or error message
        """
        
        # Get access token
        access_token = self.get_access_token()
        if not access_token:
            return {'status': 'error', 'message': 'Failed to get access token'}
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password: Base64(ShortCode + Passkey + Timestamp)
        data_to_encode = f"{self.business_short_code}{self.passkey}{timestamp}"
        password = base64.b64encode(data_to_encode.encode()).decode()
        
        # Prepare request body
        payload = {
            "BusinessShortCode": self.business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"{account_reference}_{house_id}_{user_id}",
            "TransactionDesc": f"Booking payment for house {house_id}"
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.stk_push_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ResponseCode') == '0':
                return {
                    'status': 'success',
                    'message': 'STK Push sent successfully',
                    'checkout_request_id': result.get('CheckoutRequestID'),
                    'response_code': result.get('ResponseCode'),
                    'response_description': result.get('ResponseDescription')
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('ResponseDescription', 'STK Push failed'),
                    'response_code': result.get('ResponseCode')
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Request error: {str(e)}'
            }
    
    def format_phone_number(self, phone):
        """
        Format phone number to M-Pesa format (254XXXXXXXXX)
        Accepts formats like:
        - 0722123456
        - 254722123456
        - +254722123456
        """
        # Remove any non-digit characters except the first character if it's a +
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        
        # If starts with 0, replace with 254
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        
        # If doesn't start with 254, add it
        if not phone.startswith('254'):
            phone = '254' + phone
        
        return phone


# Singleton instance
mpesa_service = MpesaService()
