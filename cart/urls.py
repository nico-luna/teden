from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/mercadopago/<int:product_id>/', views.pagar_con_mercadopago, name='pagar_con_mercadopago'),
    path('checkout/mercadopago/success/', views.checkout_success, name='checkout_success'),
    path('checkout/mercadopago/failure/', views.checkout_failure, name='checkout_failure'),
    path('checkout/mercadopago/pending/', views.checkout_pending, name='checkout_pending'),
    # path('checkout/mercadopago/ipn/', views.checkout_ipn, name='checkout_ipn'),
    # path('checkout/mercadopago/webhook/', views.checkout_webhook, name='checkout_webhook'),
    # path('checkout/mercadopago/return/', views.checkout_return, name='checkout_return'),
    # path('checkout/mercadopago/cancel/', views.checkout_cancel, name='checkout_cancel'),
    # path('checkout/mercadopago/notification/', views.checkout_notification, name='checkout_notification'),
    # path('checkout/mercadopago/redirect/', views.checkout_redirect, name='checkout_redirect'),
    # path('checkout/mercadopago/redirect/success/', views.checkout_redirect_success, name='checkout_redirect_success'),
    # path('checkout/mercadopago/redirect/failure/', views.checkout_redirect_failure, name='checkout_redirect_failure'),
    path('checkout/stripe/<int:product_id>/', views.stripe_checkout, name='stripe_checkout'),
]
