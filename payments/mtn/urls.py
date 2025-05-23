# payments/mtn/urls.py
from django.urls import path
from .views import mtn_checkout

urlpatterns = [
    path('', mtn_checkout, name='mtn_checkout'),
]
