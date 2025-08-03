# payments/urls.py
from django.urls import path
from .views import mercadopago_webhook

urlpatterns = [
    path('checkout/mercadopago/webhook/', mercadopago_webhook, name='mercadopago_webhook'),
]
