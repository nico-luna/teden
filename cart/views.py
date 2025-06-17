from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings

from orders.models import Order
from .models import Cart, CartItem
from products.models import Product

import mercadopago
import stripe

from .forms import BillingForm
from .models import BillingInfo
from django.db.models import Max

def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart = get_user_cart(request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()
        return redirect('cart_detail')
    return redirect('home')

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
    if not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('cart_detail')

    billing_info = None

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            billing_info = form.save(commit=False)
            billing_info.user = request.user
            billing_info.save()

            request.session['billing_info_id'] = billing_info.id
            return redirect('checkout_payment')
    else:
        form = BillingForm()

    return render(request, 'cart/checkout.html', {'cart': cart, 'form': form})

@login_required
def checkout_payment(request):
    cart = get_user_cart(request.user)
    billing_id = request.session.get('billing_info_id')

    if not billing_id:
        return redirect('checkout')

    billing_info = get_object_or_404(BillingInfo, id=billing_id, user=request.user)

    return render(request, 'cart/checkout_payment.html', {
        'cart': cart,
        'billing': billing_info,
    })

@login_required
def checkout_success(request):
    last_orders = Order.objects.filter(buyer=request.user).order_by('-created_at')[:10]
    return render(request, 'cart/checkout_success.html', {'orders': last_orders})

def checkout_failure(request):
    return render(request, 'cart/checkout_failure.html')

def checkout_pending(request):
    return render(request, 'cart/checkout_pending.html')

@csrf_exempt
def checkout_ipn(request):
    return HttpResponse(status=200)

@csrf_exempt
def checkout_webhook(request):
    return HttpResponse("Webhook recibido", status=200)

def checkout_return(request):
    return render(request, 'cart/checkout_return.html')

def checkout_cancel(request):
    return render(request, 'cart/checkout_cancel.html')

@login_required
def pagar_con_mercadopago_checkout(request):
    cart = get_user_cart(request.user)

    if not cart.items.exists():
        return HttpResponse("⚠️ El carrito está vacío.")

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    items = []
    for item in cart.items.all():
        items.append({
            "title": item.product.name,
            "quantity": item.quantity,
            "unit_price": float(item.product.price),
            "currency_id": "ARS",
        })

    preference_data = {
        "items": items,
        "back_urls": {
            "success": "https://teden.onrender.com/cart/checkout/mercadopago/success/",
            "failure": "https://teden.onrender.com/cart/checkout/mercadopago/failure/",
            "pending": "https://teden.onrender.com/cart/checkout/mercadopago/pending/"
        },
        "auto_return": "approved",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        payment_url = preference_response.get("response", {}).get("init_point")

        if not payment_url:
            return HttpResponse(f"❌ No se pudo obtener el enlace de pago. Detalle: {preference_response}")

        return redirect(payment_url)

    except Exception as e:
        return HttpResponse(f"❌ Error al generar preferencia: {str(e)}")

@login_required
def stripe_checkout_checkout(request):
    cart = get_user_cart(request.user)
    if not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('cart_detail')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    line_items = []
    for item in cart.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),
            },
            'quantity': item.quantity,
        })

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='https://teden.onrender.com/cart/checkout/mercadopago/success/',
            cancel_url='https://teden.onrender.com/cart/checkout/mercadopago/cancel/',
        )
        return redirect(session.url)
    except Exception as e:
        return HttpResponse(f"⚠️ Error al generar sesión de Stripe: {str(e)}")

@login_required
def confirm_order(request):
    cart = get_user_cart(request.user)
    billing_id = request.session.get('billing_info_id')

    if not billing_id or not cart.items.exists():
        messages.error(request, "No hay información de facturación o el carrito está vacío.")
        return redirect('checkout')

    billing_info = get_object_or_404(BillingInfo, id=billing_id, user=request.user)

    for item in cart.items.all():
        last_number = Order.objects.aggregate(Max('order_number'))['order_number__max'] or 0
        new_number = int(last_number) + 1

        Order.objects.create(
            buyer=request.user,
            seller=item.product.seller,
            product=item.product,
            quantity=item.quantity,
            total_price=item.total_price,
            order_number=new_number,
            billing_info=billing_info,
        )

    cart.items.all().delete()
    del request.session['billing_info_id']

    return redirect('checkout_success')

#pago en efectivo (prueba)

@login_required
def pagar_en_efectivo(request):
    cart = get_user_cart(request.user)
    billing_id = request.session.get('billing_info_id')

    if not billing_id or not cart.items.exists():
        messages.error(request, "Faltan datos o el carrito está vacío.")
        return redirect('checkout')

    billing_info = get_object_or_404(BillingInfo, id=billing_id, user=request.user)

    from django.db.models import Max
    for item in cart.items.all():
            last_order_id = Order.objects.count() + 1
    for item in cart.items.all():
        new_number = f"TEDEN-{last_order_id}-{item.product.id}"

        Order.objects.create(
            buyer=request.user,
            seller=item.product.seller,
            product=item.product,
            quantity=item.quantity,
            total_price=item.total_price,
            order_number=new_number,
            billing_info=billing_info,
        )

    cart.items.all().delete()
    del request.session['billing_info_id']
    messages.success(request, "Orden generada en modo prueba (pago en efectivo).")

    return redirect('checkout_success')