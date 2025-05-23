# payments/mtn/momo_client.py
import requests
from django.conf import settings

class MTNMomoAPI:
    def __init__(self):
        self.subscription_key = settings.MTN_SUBSCRIPTION_KEY
        self.api_user = settings.MTN_API_USER
        self.api_key = settings.MTN_API_KEY
        self.base_url = "https://sandbox.momodeveloper.mtn.com"
        self.token = self.get_access_token()

    def get_access_token(self):
        url = f"{self.base_url}/collection/token/"
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Authorization": f"Basic {self.api_user}:{self.api_key}"
        }
        response = requests.post(url, headers=headers)
        return response.json().get("access_token")

    def request_payment(self, amount, phone_number, external_id, currency='ZMW'):
        url = f"{self.base_url}/collection/v1_0/requesttopay"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Target-Environment": "sandbox",
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "X-Reference-Id": external_id,
            "Content-Type": "application/json"
        }
        data = {
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": "EHC-Marketplace Purchase",
            "payeeNote": "Thank you"
        }
        return requests.post(url, headers=headers, json=data)
