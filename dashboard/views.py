from django.shortcuts import render
from django.db import models
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from .decorators import seller_required
from django.shortcuts import render, redirect
from store.models import Store
from products.models import Product, Category
from orders.models import Order
from django.shortcuts import render, redirect
from django.db import models
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .decorators import seller_required
from store.models import Store
from products.models import Product, Category
from orders.models import Order
from appointments.models import Appointment, Service


@login_required
@seller_required
def dashboard_seller(request):
    # Obtener tienda (puede ser None). Permitimos ver el dashboard aunque no
    # exista tienda y mostramos una CTA para crearla.
    store = Store.objects.filter(owner=request.user).first()
    no_store = store is None

    product_count = Product.objects.filter(seller=request.user).count() if not no_store else 0
    published_count = Product.objects.filter(seller=request.user, is_active=True).count() if not no_store else 0
    category_count = Category.objects.count()
    public_url_obj = getattr(request.user, 'store_profile', None)
    public_url = public_url_obj.slug if public_url_obj else None
    total_sales = Order.objects.filter(seller=request.user, status='completed').aggregate(total=models.Sum('total_price'))['total'] or 0
    appointment_count = Appointment.objects.filter(vendor=request.user).count() if not no_store else 0
    commission_percent = getattr(request.user.sellerprofile.plan, 'commission_percent', 0)
    profit = float(total_sales) * (1 - commission_percent / 100) if total_sales else 0
    services = Service.objects.filter(
        is_active=True,
        vendor__sellerprofile__mercadopagocredential__isnull=False
    )

    return render(request, 'dashboard/dashboard_seller.html', {
        'store': store,
        'product_count': product_count,
        'published_count': published_count,
        'category_count': category_count,
        'public_url': public_url,
        'total_sales': total_sales,
        'appointment_count': appointment_count,
        'profit': profit,
        'no_store': no_store,
        'services': services,
    })


@login_required
def dashboard_buyer(request):
    if request.user.role != 'buyer':
        return redirect('dashboard_seller')

    return render(request, 'core/home.html')


@login_required
@seller_required
def dashboard_stats_api(request):
    # Solo vendedores con perfil pueden consultar estadísticas
    store = Store.objects.filter(owner=request.user).first()
    no_store = store is None

    product_count = Product.objects.filter(seller=request.user).count() if not no_store else 0
    published_count = Product.objects.filter(seller=request.user, is_active=True).count() if not no_store else 0
    category_count = Category.objects.count()
    total_sales = Order.objects.filter(seller=request.user, status='completed').aggregate(total=models.Sum('total_price'))['total'] or 0
    appointment_count = Appointment.objects.filter(vendor=request.user).count() if not no_store else 0
    commission_percent = getattr(request.user.sellerprofile.plan, 'commission_percent', 0)
    profit = float(total_sales) * (1 - commission_percent / 100) if total_sales else 0

    return JsonResponse({
        'product_count': product_count,
        'published_count': published_count,
        'category_count': category_count,
        'total_sales': float(total_sales),
        'appointment_count': appointment_count,
        'profit': float(profit),
    })


@login_required
@seller_required
def seller_products(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'dashboard/seller_products.html', {'products': products})

