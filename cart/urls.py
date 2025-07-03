from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # 🧾 Checkout del carrito
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/confirm/', views.confirm_order, name='confirm_order'),

    # 🧾 Métodos de pago para el carrito completo
    path('checkout/mercadopago/', views.pagar_con_mercadopago_checkout, name='pagar_con_mercadopago_checkout'),
    path('checkout/stripe/', views.stripe_checkout_checkout, name='pagar_con_stripe_checkout'),


    # 🎯 Resultados pagos
    path('checkout/mercadopago/links/', views.checkout_links_mp, name='checkout_links_mp'),
    path('checkout/mercadopago/success/', views.checkout_success, name='checkout_success'),
    path('checkout/mercadopago/failure/', views.checkout_failure, name='checkout_failure'),
    path('checkout/mercadopago/pending/', views.checkout_pending, name='checkout_pending'),
    path('checkout/mercadopago/webhook/', views.checkout_webhook, name='checkout_webhook'),
    path('checkout/mercadopago/return/', views.checkout_return, name='checkout_return'),
    path('checkout/mercadopago/cancel/', views.checkout_cancel, name='checkout_cancel'),

    # 🧾 Checkout individual por producto (opcional)
    # path('checkout/mercadopago/<int:product_id>/', views.pagar_con_mercadopago, name='pagar_con_mercadopago_individual'),
    # path('checkout/stripe/<int:product_id>/', views.stripe_checkout, name='pagar_con_stripe_individual'),

    # Pago en efectivo
    path('checkout/efectivo/', views.pagar_en_efectivo, name='pagar_en_efectivo'),

]