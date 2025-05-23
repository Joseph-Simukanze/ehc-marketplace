# payments/mtn/views.py
import uuid
from django.shortcuts import render, redirect
from .momo_client import MTNMomoAPI
from django.contrib import messages

def mtn_checkout(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        phone_number = request.POST['phone']
        transaction_id = str(uuid.uuid4())
        mtn = MTNMomoAPI()
        response = mtn.request_payment(amount, phone_number, transaction_id)

        if response.status_code == 202:
            messages.success(request, "Payment request sent. Awaiting confirmation.")
            return redirect('payment_success')
        else:
            messages.error(request, "Payment failed or was not accepted.")
            return redirect('payment_error')

    return render(request, 'payments/mtn_checkout.html')
