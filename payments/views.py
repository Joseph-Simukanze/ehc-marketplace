# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

from .models import Payment
from marketplace.models import Order
from .forms import PaymentForm
from .utils import generate_transaction_id
from .gateways import MTNPaymentGateway, AirtelPaymentGateway

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import random
import string
import requests


@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    if hasattr(order, 'payment_detail'):
        return redirect('payments:verify_payment', payment_id=order.payment_detail.id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        phone_number = request.POST.get('phone_number')
        transaction_id = generate_transaction_id()

        while Payment.objects.filter(transaction_id=transaction_id).exists():
            transaction_id = generate_transaction_id()

        gateways = {
            'mtn': MTNPaymentGateway,
            'airtel': AirtelPaymentGateway,
        }

        if payment_method not in gateways:
            messages.error(request, "Invalid payment method selected.")
            return render(request, 'payments/process_payment.html', {'order': order})

        gateway = gateways[payment_method]()
        response = gateway.initiate_payment(phone_number, float(order.total_amount), transaction_id)

        if response.get('status') == 'SUCCESS':
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total_amount,
                transaction_id=transaction_id,
                phone=phone_number,
                status='pending'
            )
            messages.success(request, f"{payment_method.upper()} payment initiated. Please check your phone.")
            return redirect('payments:verify_payment', payment_id=payment.id)
        else:
            messages.error(request, response.get('message', 'Payment failed. Please try again.'))

    return render(request, 'payments/process_payment.html', {'order': order})


@login_required
def verify_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if payment.order.buyer != request.user:
        messages.error(request, "Unauthorized access")
        return redirect('marketplace:home')

    if payment.is_verified:
        return redirect('payments:payment_success_by_id', payment_id=payment.id)

    if request.method == 'POST':
        gateway = MTNPaymentGateway() if payment.payment_method == 'mtn' else AirtelPaymentGateway()
        response = gateway.check_payment_status(payment.transaction_id)

        if response.get('status') == 'SUCCESS':
            payment.is_verified = True
            payment.save()

            payment.order.status = 'processing'
            payment.order.save()

            return redirect('payments:payment_success_by_id', payment_id=payment.id)
        else:
            messages.error(request, "Payment not completed yet")

    return render(request, 'payments/verify_payment.html', {'payment': payment})


@login_required
def payment_success_by_id(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, is_verified=True)

    if payment.order and payment.order.buyer != request.user:
        messages.error(request, "Unauthorized access")
        return redirect('marketplace:home')

    return render(request, 'payments/payment_success.html', {'payment': payment})


def payment_success(request, transaction_id):
    payment = get_object_or_404(Payment, transaction_id=transaction_id, is_verified=True)
    return render(request, 'payments/payment_success.html', {'payment': payment})


def payment_failed(request, transaction_id):
    payment = get_object_or_404(Payment, transaction_id=transaction_id)
    return render(request, 'payments/payment_failed.html', {'payment': payment})


def simulate_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.transaction_id = generate_fake_transaction_id()
            payment.is_verified = random.choices([True, False], weights=[70, 30])[0]
            payment.save()

            if payment.is_verified:
                return redirect('payments:payment_success', transaction_id=payment.transaction_id)
            else:
                return redirect('payments:payment_failed', transaction_id=payment.transaction_id)
    else:
        form = PaymentForm()

    return render(request, 'payments/simulate_payment.html', {'form': form})


def simulate_subscription_payment(request, user_id):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            subscription_payment = form.save(commit=False)
            subscription_payment.user = user
            subscription_payment.transaction_id = generate_fake_transaction_id()
            subscription_payment.is_verified = random.choices([True, False], weights=[70, 30])[0]
            subscription_payment.save()

            if subscription_payment.is_verified:
                return redirect('payments:payment_success', transaction_id=subscription_payment.transaction_id)
            else:
                return redirect('payments:payment_failed', transaction_id=subscription_payment.transaction_id)
    else:
        form = PaymentForm()

    return render(request, 'payments/simulate_subscription_payment.html', {'form': form, 'user': user})


def payment_page(request):
    return render(request, 'payments/payment.html')


def generate_fake_transaction_id():
    return 'TXN_' + ''.join(random.choices(string.digits, k=8))


def generate_receipt(request, transaction_id):
    payment = get_object_or_404(Payment, transaction_id=transaction_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{transaction_id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"Receipt for Payment {payment.transaction_id}")
    p.drawString(100, 730, f"Amount: ZMW {payment.amount}")
    p.drawString(100, 710, f"Payment Method: {payment.get_payment_method_display()}")
    p.drawString(100, 690, f"Date: {payment.payment_date}")
    p.showPage()
    p.save()

    return response


def mtn_test_request(request):
    headers = {
        'Ocp-Apim-Subscription-Key': settings.MTN_PRIMARY_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.get(
        'https://sandbox.momodeveloper.mtn.com/your-api-endpoint',
        headers=headers
    )

    print(response.json())
    return JsonResponse(response.json())


def payment_successful(request):
    return render(request, 'payments/payment_successful.html')


# Example redirect usage
def some_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return redirect(reverse('payments:process_payment', kwargs={'order_id': order.id}))

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payments/order_details.html', {'order': order})

# views.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER
from django.http import HttpResponse
from .models import Payment
import os
from django.conf import settings

def generate_receipt(request, order_id):
    payment = Payment.objects.get(order_id=order_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="EHC_Receipt_{order_id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Set up custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=14,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=24
    )

    # Background color
    p.saveState()
    p.setFillColor(colors.HexColor('#f8f9fa'))
    p.rect(0, 0, width, height, fill=1, stroke=0)
    p.restoreState()

    # Content background
    p.saveState()
    p.setFillColor(colors.white)
    p.roundRect(20*mm, 20*mm, width - 40*mm, height - 40*mm, 5*mm, fill=1, stroke=0)
    p.restoreState()

    # Logo
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'ehc_logo.png')
    if os.path.exists(logo_path):
        logo_width = 45*mm
        logo_height = 15*mm
        p.drawImage(logo_path, 
                    width - 20*mm - logo_width,
                    height - 25*mm,
                    width=logo_width, 
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto')

    # Header
    title = Paragraph("PAYMENT RECEIPT", title_style)
    title.wrapOn(p, width - 40*mm, 50)
    title.drawOn(p, 20*mm, height - 35*mm)

    subtitle = Paragraph("EHC Marketplace | Official Transaction Document", subtitle_style)
    subtitle.wrapOn(p, width - 40*mm, 50)
    subtitle.drawOn(p, 20*mm, height - 50*mm)

    # Decorative line
    p.setStrokeColor(colors.HexColor('#3498db'))
    p.setLineWidth(0.5*mm)
    p.line(20*mm, height - 60*mm, width - 20*mm, height - 60*mm)

    # Company info
    p.setFont("Helvetica", 9)
    p.setFillColor(colors.HexColor('#7f8c8d'))
    p.drawString(20*mm, height - 75*mm, "📍 123 Business Street, Lusaka, Zambia")
    p.drawString(20*mm, height - 85*mm, "📞 +260 XXX XXX XXX")
    p.drawString(20*mm, height - 95*mm, "📧 support@ehcmarketplace.com")
    p.drawString(20*mm, height - 105*mm, "🆔 VAT: XXXXXXX")

    # Transaction details header
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(colors.HexColor('#2c3e50'))
    p.drawString(20*mm, height - 125*mm, "TRANSACTION DETAILS")

    # Payment details table data
    data = [
        ["Order ID:", str(payment.order.id)],
        ["Payment Method:", payment.get_payment_method_display()],
        ["Amount Paid:", f"ZMW {payment.amount:,.2f}"],
        ["Transaction ID:", payment.transaction_id],
        ["Payment Date:", payment.payment_date.strftime('%B %d, %Y %H:%M')],
        ["Status:", "COMPLETED"]
    ]

    table = Table(data, colWidths=[5 * cm, 10 * cm])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4a90e2')),  # Left col blue background
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),                # Left col white text
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#dbe9f7')), # Right col light blue
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),                # Right col black text
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw the table on the canvas
    table.wrapOn(p, width - 40*mm, height)
    table.drawOn(p, 20*mm, height - 170*mm)

    # Thank you message background
    p.saveState()
    p.setFillColor(colors.HexColor('#f1f9fe'))
    p.roundRect(20*mm, height - 200*mm, width - 40*mm, 15*mm, 3*mm, fill=1, stroke=0)
    p.restoreState()
    
    # Thank you message text
    p.setFont("Helvetica-Oblique", 12)
    p.setFillColor(colors.HexColor('#3498db'))
    p.drawCentredString(width / 2, height - 195*mm, "Thank you for your purchase with EHC Marketplace!")

    # Footer background
    p.saveState()
    p.setFillColor(colors.HexColor('#2c3e50'))
    p.rect(0, 0, width, 20*mm, fill=1, stroke=0)
    p.restoreState()

    # Footer text
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.white)
    p.drawCentredString(width / 2, 14*mm, "This is an official receipt. Please keep it for your records.")
    p.drawCentredString(width / 2, 9*mm, f"Document generated on {payment.payment_date.strftime('%Y-%m-%d %H:%M')}")
    p.drawCentredString(width /2, 5*mm, "for any queries email us On josephsimukanze@gmail.com/ call 0777672440")

    # Watermark
    p.saveState()
    p.setFont("Helvetica", 72)
    p.setFillColor(colors.HexColor('#f1f5f9'))
    p.setFillAlpha(0.08)
    p.rotate(45)
    p.drawCentredString(width / 2 + 50*mm, -50*mm, "PAID")
    p.restoreState()

    # Security dots at bottom
    p.setFont("Helvetica", 6)
    p.setFillColor(colors.HexColor('#bdc3c7'))
    for i in range(1, int(width / mm)):
        p.drawString(i * mm, 2*mm, "•")

    p.showPage()
    p.save()

    return response


from django.shortcuts import render

def order_list(request):
    # Dummy order data for now – you can replace this with real data from your models
    orders = [
        {'id': 1, 'item': 'Wireless Earbuds', 'status': 'Delivered', 'amount': 150},
        {'id': 2, 'item': 'USB-C Charger', 'status': 'Pending', 'amount': 80},
        {'id': 3, 'item': 'Laptop Stand', 'status': 'Shipped', 'amount': 220},
    ]
    return render(request, 'payments/order_list.html', {'orders': orders})

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Payment  # adjust this if your model name is different

def generate_invoice(request, order_id):
    # Replace Payment with your actual model if needed
    payment = get_object_or_404(Payment, id=order_id)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/generate_invoice.html', context)


def faq(request):
    return render(request, 'payments/faq.html')
