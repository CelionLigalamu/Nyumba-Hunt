# M-Pesa Daraja Integration Setup Guide

## Overview
This guide explains how to set up M-Pesa Daraja STK Push integration for the Nyumba Hunt application.

## What is M-Pesa Daraja?
M-Pesa Daraja is Safaricom's API platform that allows developers to integrate M-Pesa payments into their applications. STK Push sends a payment prompt directly to the customer's phone.

## Prerequisites
1. A Safaricom M-Pesa Business Account
2. Daraja API credentials (Consumer Key, Consumer Secret, Business Short Code, Passkey)

## Getting Daraja Credentials

### Step 1: Create Developer Account
1. Visit https://developer.safaricom.co.ke/
2. Sign up for a developer account
3. Create an application

### Step 2: Get Credentials
From your Daraja dashboard, collect:
- **Consumer Key**: Your API consumer key
- **Consumer Secret**: Your API consumer secret  
- **Business Short Code**: Your M-Pesa business short code (e.g., 174379 for sandbox)
- **Passkey**: Your M-Pesa passkey

## Configuration

### Update settings.py
Edit `nyumbaProject/settings.py` and update these values:

```python
MPESA_ENVIRONMENT = 'sandbox'  # Use 'sandbox' for testing, 'production' for live
MPESA_BUSINESS_SHORT_CODE = '174379'  # Your business short code
MPESA_CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
MPESA_CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd1a2c2f2f'
MPESA_CALLBACK_URL = 'https://yourdomain.com/payment/callback/'
```

### Update Callback URL
1. Go to your Daraja app settings
2. Set the Callback URL to: `https://yourdomain.com/payment/callback/`
3. This URL will receive payment confirmation from M-Pesa

## How It Works

### User Flow
1. User books a house
2. User is redirected to payment page
3. User enters M-Pesa phone number
4. System sends STK Push to user's phone
5. User sees M-Pesa payment prompt
6. User enters M-Pesa PIN to complete payment
7. Payment is confirmed via callback
8. Booking is marked as confirmed

### Payment Endpoints
- **Initiate Payment**: `/payment/<booking_id>/`
- **Payment Callback**: `/payment/callback/` (POST from M-Pesa)

## Testing

### Using Sandbox
1. Use `MPESA_ENVIRONMENT = 'sandbox'`
2. Business Short Code: `174379`
3. Test phone number: `254708374149` (Safaricom test number)

### Test Flow
1. Book a house
2. Go to payment page
3. Enter test phone number
4. Check M-Pesa for prompt (may not appear in sandbox, but API validates correctly)

## For Production

1. Change `MPESA_ENVIRONMENT = 'production'`
2. Get your production credentials from Safaricom
3. Update all credentials in settings.py
4. Set your actual domain in CALLBACK_URL
5. Ensure your domain has valid SSL certificate
6. Test with real users

## Troubleshooting

### "Access Token" Error
- Check Consumer Key and Consumer Secret
- Verify they are for the correct environment (sandbox/production)

### "Invalid phone number" Error
- Phone must be in format: 254XXXXXXXXX
- System auto-converts: 0722123456 → 254722123456

### Callback Not Received
- Ensure CALLBACK_URL is publicly accessible
- Check that SSL certificate is valid
- Verify firewall isn't blocking POST requests

## Files Created/Modified

### New Files
- `housesApp/mpesa_service.py` - M-Pesa API service
- `housesApp/templates/housesApp/payment.html` - Payment form
- `housesApp/migrations/0002_*.py` - Database migration

### Modified Files
- `housesApp/models.py` - Added Payment model
- `housesApp/views.py` - Added payment views
- `housesApp/forms.py` - Added PaymentForm
- `housesApp/urls.py` - Added payment URLs
- `housesApp/admin.py` - Registered Payment model
- `housesApp/templates/housesApp/book.html` - Improved booking form
- `nyumbaProject/settings.py` - Added M-Pesa settings

## Support
For issues with Daraja API, visit: https://developer.safaricom.co.ke/docs
