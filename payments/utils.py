import requests
import json
import uuid
from django.conf import settings

class MTNPaymentGateway:
    def __init__(self):
        self.api_key = settings.MTN_API_KEY
        self.api_secret = settings.MTN_API_SECRET
        self.base_url = settings.MTN_API_URL
    
    def initiate_payment(self, phone_number, amount, reference):
        """Initiates payment through MTN Mobile Money"""
        # In a real implementation, this would make an API call to MTN
        # For now, we'll simulate a successful response
        
        return {
            'status': 'SUCCESS',
            'reference': reference,
            'message': 'Payment initiated successfully'
        }
    
    def check_payment_status(self, reference):
        """Checks the status of a payment"""
        # In a real implementation, this would make an API call to MTN
        # For now, we'll simulate a successful response
        
        return {
            'status': 'SUCCESSFUL',
            'reference': reference,
            'message': 'Payment completed successfully'
        }

class AirtelPaymentGateway:
    def __init__(self):
        self.api_key = settings.AIRTEL_API_KEY
        self.api_secret = settings.AIRTEL_API_SECRET
        self.base_url = settings.AIRTEL_API_URL
    
    def initiate_payment(self, phone_number, amount, reference):
        """Initiates payment through Airtel Money"""
        # In a real implementation, this would make an API call to Airtel
        # For now, we'll simulate a successful response
        
        return {
            'status': 'SUCCESS',
            'reference': reference,
            'message': 'Payment initiated successfully'
        }
    
    def check_payment_status(self, reference):
        """Checks the status of a payment"""
        # In a real implementation, this would make an API call to Airtel
        # For now, we'll simulate a successful response
        
        return {
            'status': 'SUCCESSFUL',
            'reference': reference,
            'message': 'Payment completed successfully'
        }

def generate_transaction_id():
    """Generate a unique transaction ID"""
    return str(uuid.uuid4())


import requests
from django.conf import settings

def call_mtn_api():
    headers = {
        'Ocp-Apim-Subscription-Key': settings.MTN_PRIMARY_KEY,
        'Content-Type': 'application/json'
    }

    url = 'https://sandbox.momodeveloper.mtn.com/collection/token/'  # Example endpoint
    response = requests.get(url, headers=headers)

    try:
        return response.json()
    except Exception as e:
        return {"error": str(e), "status_code": response.status_code}
