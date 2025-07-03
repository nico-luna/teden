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

# Utilidad para obtener o crear el carrito de un usuario
def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

# Agrega un producto al carrito del usuario
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

# Vista que muestra el detalle del carrito
@login_required
def cart_detail(request):
    cart = get_user_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

# Elimina un item del carrito
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_detail')

# Vista de checkout donde se completan los datos de facturación
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

# Vista intermedia para mostrar la info antes del pago
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

# Vista de éxito post pago
@login_required
def checkout_success(request):
    last_orders = Order.objects.filter(buyer=request.user).order_by('-created_at')[:10]
    return render(request, 'cart/checkout_success.html', {'orders': last_orders})

# Otras vistas simples de resultado

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

# Checkout de MercadoPago (actualmente sin application_fee ni separación por vendedor)
from collections import defaultdict
from payments.utils import crear_preferencia_para_vendedor

@login_required
def pagar_con_mercadopago_checkout(request):
    cart = get_user_cart(request.user)
    if not cart.items.exists():
        messages.error(request, "El carrito está vacío.")
        return redirect('cart_detail')

    productos_por_vendedor = defaultdict(list)

    for item in cart.items.all():
        seller = item.product.seller
        productos_por_vendedor[seller].append({
            "title": item.product.name,
            "quantity": item.quantity,
            "unit_price": float(item.product.price),
            "currency_id": "ARS"
        })

    preferencias = []

    try:
        for vendedor, items in productos_por_vendedor.items():
            link_pago = crear_preferencia_para_vendedor(
                seller=vendedor,
                items=items,
                buyer_email=request.user.email
            )
            preferencias.append({
                "vendedor": vendedor,
                "link": link_pago
            })

        # Guardar en sesión y mostrar en nueva vista
        request.session['links_de_pago'] = preferencias
        return redirect('checkout_links_mp')

    except Exception as e:
        return HttpResponse(f"❌ Error: {e}")

# Checkout con Stripe (modo test)
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

# Confirmación final del pedido (luego del pago)
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

# Pago en efectivo para testing
@login_required
def pagar_en_efectivo(request):
    cart = get_user_cart(request.user)
    billing_id = request.session.get('billing_info_id')

    if not billing_id or not cart.items.exists():
        messages.error(request, "Faltan datos o el carrito está vacío.")
        return redirect('checkout')

    billing_info = get_object_or_404(BillingInfo, id=billing_id, user=request.user)

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

# Vista para mostrar los links de pago generados
@login_required
def checkout_links_mp(request):
    links = request.session.get('links_de_pago', [])

    if not links:
        messages.error(request, "No hay enlaces de pago disponibles.")
        return redirect('cart_detail')

    return render(request, 'cart/checkout_links_mp.html', {'links': links})