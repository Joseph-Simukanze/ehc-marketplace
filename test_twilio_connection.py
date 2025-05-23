import requests

response = requests.get('https://verify.twilio.com')
print(response.status_code)
