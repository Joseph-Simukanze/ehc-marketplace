from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment verification and processing
    path('verify/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),

    # Payment simulation & test (e.g., MTN)
    path('simulate/', views.simulate_payment, name='simulate_payment'),
    path('test-mtn/', views.mtn_test_request, name='mtn_test_request'),
    path('', views.mtn_test_request, name='mtn_test'),  # Default test route

    # Success and failure views
    path('success/', views.payment_successful, name='payment_successful'),  # generic
    path('success/<int:payment_id>/', views.payment_success_by_id, name='payment_success_by_id'),  # by ID
    path('success/<str:transaction_id>/', views.payment_success, name='payment_success'),  # by transaction ID
    path('failed/<str:transaction_id>/', views.payment_failed, name='payment_failed'),
    path('payments/order/<int:order_id>/', views.order_details, name='order_details'),
    # Receipt
    path('generate_receipt/<str:transaction_id>/', views.generate_receipt, name='generate_receipt'),
    path('payments/generate_receipt/<int:order_id>/', views.generate_receipt, name='generate_receipt'),
    path('orders/', views.order_list, name='order_list'),
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
    path('faq/', views.faq, name='faq'),

]
