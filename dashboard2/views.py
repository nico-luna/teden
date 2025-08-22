from django.shortcuts import render
from django.db import models
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from store.models import Store
from products.models import Product, Category
from orders.models import Order
from appointments.models import Appointment

@login_required
def dashboard_seller(request):
    # Si no es vendedor, mostrar mensaje y opción para convertirse en vendedor
    # Si el usuario tiene rol seller pero no tiene SellerProfile, lo creamos automáticamente
    if request.user.role == 'seller' and not hasattr(request.user, 'sellerprofile'):
        from plans.models import SellerProfile, SellerPlan
        starter_plan = SellerPlan.objects.filter(name='starter').first()
        SellerProfile.objects.create(user=request.user, plan=starter_plan)

    not_seller = request.user.role != 'seller' or not hasattr(request.user, 'sellerprofile')
    if not_seller:
        return redirect('convertirse_en_vendedor')
    # Si no tiene tienda, mostrar mensaje y opción para crear tienda
    if not hasattr(request.user, 'store'):
        return render(request, 'dashboard/dashboard_seller.html', {
            'no_store': True,
        })

    store = Store.objects.filter(owner=request.user).first()
    product_count = Product.objects.filter(seller=request.user).count()
    published_count = Product.objects.filter(seller=request.user, is_active=True).count()
    category_count = Category.objects.count()
    public_url = getattr(request.user.store_profile, 'slug', None) if hasattr(request.user, 'store_profile') else None
    total_sales = Order.objects.filter(seller=request.user, status='completed').aggregate(total=models.Sum('total_price'))['total'] or 0
    appointment_count = Appointment.objects.filter(vendor=request.user).count()
    commission_percent = getattr(request.user.sellerprofile.plan, 'commission_percent', 0)
    profit = total_sales * (1 - commission_percent / 100) if total_sales else 0
    return render(request, 'dashboard/dashboard_seller.html', {
        'not_seller': False,
        'store': store,
        'product_count': product_count,
        'published_count': published_count,
        'category_count': category_count,
        'public_url': public_url,
        'total_sales': total_sales,
        'appointment_count': appointment_count,
        'profit': profit,
    })


@login_required
def dashboard_buyer(request):
    if request.user.role != 'buyer':
        return redirect('dashboard_seller')

    return render(request, 'core/home.html')

@login_required
def dashboard_stats_api(request):
    product_count = Product.objects.filter(seller=request.user).count()
    published_count = Product.objects.filter(seller=request.user, is_active=True).count()
    category_count = Category.objects.count()
    total_sales = Order.objects.filter(seller=request.user, status='completed').aggregate(total=models.Sum('total_price'))['total'] or 0
    appointment_count = Appointment.objects.filter(vendor=request.user).count()
    commission_percent = getattr(request.user.sellerprofile.plan, 'commission_percent', 0)
    profit = total_sales * (1 - commission_percent / 100) if total_sales else 0
    return JsonResponse({
        'product_count': product_count,
        'published_count': published_count,
        'category_count': category_count,
        'total_sales': total_sales,
        'appointment_count': appointment_count,
        'profit': profit,
    })
