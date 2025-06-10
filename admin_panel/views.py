from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db.models import Q  # Para filtros dinámicos
from products.models import Product  # Asegurate de que el modelo se llama así

User = get_user_model()

@staff_member_required
def dashboard_admin(request):
    return render(request, 'admin_panel/dashboard.html')


@staff_member_required
def manage_users(request):
    query = request.GET.get('q')
    role = request.GET.get('role')
    verified = request.GET.get('verified')

    users = User.objects.all()

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))

    if role:
        users = users.filter(role=role)

    if verified == 'yes':
        users = users.filter(is_verified=True)
    elif verified == 'no':
        users = users.filter(is_verified=False)

    return render(request, 'admin_panel/manage_users.html', {'users': users})


@staff_member_required
def manage_products(request):
    query = request.GET.get('q')
    productos = Product.objects.select_related('seller').all()

    if query:
        productos = productos.filter(name__icontains=query)

    return render(request, 'admin_panel/manage_products.html', {'productos': productos})


@staff_member_required
def site_statistics(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    verified_sellers = User.objects.filter(role='seller', is_verified=True).count()

    context = {
        'total_users': total_users,
        'verified_sellers': verified_sellers,
        'total_products': total_products
    }
    return render(request, 'admin_panel/statistics.html', context)


@staff_member_required
def toggle_product(request, product_id):
    producto = Product.objects.get(id=product_id)
    producto.is_active = not producto.is_active
    producto.save()
    return redirect('manage_products')


@staff_member_required
def toggle_verification(request, user_id):
    user = User.objects.get(id=user_id)
    if user.role == 'seller':
        user.is_verified = not user.is_verified
        user.save()
    return redirect('manage_users')

@staff_member_required
def toggle_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('manage_users')
from django.http import HttpResponse

@staff_member_required
def borrar_usuarios(request):
    User = get_user_model()
    usuarios_a_borrar = User.objects.exclude(username='admin')

    # Borrar productos relacionados primero
    Product.objects.filter(seller__in=usuarios_a_borrar).delete()

    # Luego borrar los usuarios
    usuarios_a_borrar.delete()

    return HttpResponse("✅ Usuarios y productos eliminados (excepto admin).")

