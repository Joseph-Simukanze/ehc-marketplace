# payments/mtn_utils.py

from django.conf import settings
import requests

def call_mtn_api():
    headers = {
        'Ocp-Apim-Subscription-Key': settings.MTN_PRIMARY_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.get('https://sandbox.momodeveloper.mtn.com/your-api-endpoint', headers=headers)
    return response.json()
