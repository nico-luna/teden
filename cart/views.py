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
import requests

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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('{"success": true}', content_type='application/json')
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

    from payments.utils import crear_preferencia_para_vendedor
    from collections import defaultdict
    productos_por_vendedor = defaultdict(list)
    for item in cart.items.all():
        seller = item.product.seller
        productos_por_vendedor[seller].append({
            "title": item.product.name,
            "quantity": item.quantity,
            "unit_price": float(item.product.price),
            "currency_id": "ARS"
        })

    # Si hay más de un vendedor, redirigir a la lista de links
    if len(productos_por_vendedor) > 1:
        return redirect('pagar_con_mercadopago_checkout')

    # Si solo hay uno, intentar generar el link
    mercado_pago_checkout_url = None
    vendedor = next(iter(productos_por_vendedor.keys()), None)
    items = productos_por_vendedor[vendedor] if vendedor else []
    if vendedor:
        try:
            mercado_pago_checkout_url = crear_preferencia_para_vendedor(
                seller=vendedor,
                items=items,
                buyer_email=request.user.email
            )
        except Exception as e:
            mercado_pago_checkout_url = None
            messages.error(request, str(e))

    return render(request, 'cart/checkout_payment.html', {
        'cart': cart,
        'billing': billing_info,
        'mercado_pago_checkout_url': mercado_pago_checkout_url,
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
    for vendedor, items in productos_por_vendedor.items():
        total_vendedor = sum(item['unit_price'] * item['quantity'] for item in items)
        try:
            link_pago = crear_preferencia_para_vendedor(
                seller=vendedor,
                items=items,
                buyer_email=request.user.email
            )
            preferencias.append({
                "vendedor": vendedor.username,
                "link": link_pago,
                "error": None,
                "total": total_vendedor
            })
        except Exception as e:
            preferencias.append({
                "vendedor": vendedor.username,
                "link": None,
                "error": str(e),
                "total": total_vendedor
            })

    request.session['links_de_pago'] = preferencias
    return redirect('checkout_links_mp')

# Vista de pago directo por producto desde modal
@login_required
def pagar_producto_individual(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = get_user_cart(request.user)
    cart.items.all().delete()
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    return redirect('pagar_con_mercadopago_checkout')

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
                'currency': 'USD',
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
    cart = get_user_cart(request.user)
    productos_por_vendedor = {}
    totales_por_vendedor = {}
    for item in cart.items.all():
        vendedor = item.product.seller.username
        if vendedor not in productos_por_vendedor:
            productos_por_vendedor[vendedor] = []
            totales_por_vendedor[vendedor] = 0
        subtotal = item.product.price * item.quantity
        productos_por_vendedor[vendedor].append({
            'id': item.id,
            'nombre': item.product.name,
            'precio': item.product.price,
            'cantidad': item.quantity,
            'descripcion': item.product.description,
            'tamano': item.product.file.size if item.product.file else None,
            'subtotal': subtotal
        })
        totales_por_vendedor[vendedor] += subtotal

    # Consultar estado de pago en MercadoPago
    for link in links:
        estado = 'pendiente'
        if link['link']:
            try:
                import re
                m = re.search(r'/checkout/preferences/(\d+)', link['link'])
                preference_id = m.group(1) if m else None
                if preference_id:
                    url = f'https://api.mercadopago.com/checkout/preferences/{preference_id}'
                    token = settings.MERCADOPAGO_ACCESS_TOKEN
                    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
                    if resp.status_code == 200:
                        data = resp.json()
                        estado = data.get('status', 'pendiente')
            except Exception:
                estado = 'error'
        link['estado'] = estado
        link['productos'] = productos_por_vendedor.get(link['vendedor'], [])
        link['total'] = totales_por_vendedor.get(link['vendedor'], 0)

    # Permitir eliminar producto y editar cantidad
    if request.method == 'POST':
        eliminar_id = request.POST.get('eliminar_id')
        editar_id = request.POST.get('editar_id')
        nueva_cantidad = request.POST.get('nueva_cantidad')
        if eliminar_id:
            CartItem.objects.filter(id=eliminar_id, cart=cart).delete()
            return redirect('checkout_links_mp')
        if editar_id and nueva_cantidad:
            try:
                item = CartItem.objects.get(id=editar_id, cart=cart)
                item.quantity = int(nueva_cantidad)
                item.save()
            except Exception:
                pass
            return redirect('checkout_links_mp')

    return render(request, 'cart/checkout_links_mp.html', {
        'links': links,
        'ver_productos_url': '/orders/comprados/'
    })