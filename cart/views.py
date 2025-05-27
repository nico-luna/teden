from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import Product
from .forms import CheckoutForm

def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_user_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart = get_user_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = get_user_cart(request.user)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Aquí podrías crear el Order, procesar pago, enviar email, etc.
            # Por ahora vamos a vaciar el carrito y mostrar éxito:
            cart.items.all().delete()
            return render(request, 'cart/checkout_success.html', {'email': form.cleaned_data['email']})
    else:
        form = CheckoutForm()
    return render(request, 'cart/checkout.html', {'cart': cart, 'form': form})

from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from products.models import Product
import mercadopago

def pagar_con_mercadopago(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": product.name,
            "quantity": 1,
            "unit_price": float(product.price),
        }],
        "back_urls": {
            "success": "http://127.0.0.1:8000/success",
            "failure": "http://127.0.0.1:8000/failure",
            "pending": "http://127.0.0.1:8000/pending"
        },
        "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    payment_url = preference_response["response"]["init_point"]

    return redirect(payment_url)

def checkout_success(request):
    return render(request, 'cart/checkout_success.html')

def checkout_failure(request):
    return render(request, 'cart/checkout_failure.html')

def checkout_pending(request):
    return render(request, 'cart/checkout_pending.html')

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def checkout_ipn(request):
    # MercadoPago puede enviar datos POST a esta URL como notificación IPN
    return HttpResponse(status=200)

# cart/views.py
import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from products.models import Product  # O el modelo que uses

def stripe_checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),  # en centavos
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/success', 
        cancel_url='http://127.0.0.1:8000/cancel',
    )

    return redirect(session.url)  # Redirige al checkout de Stripe
