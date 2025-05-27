from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProductForm
from .models import Product

@login_required
def add_product(request):
    if request.user.role != 'seller':
        return redirect('dashboard')  # Seguridad: solo vendedores pueden acceder

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # ✅ Importante para manejar archivos (imágenes)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Product

@login_required
def inventory(request):
    if request.user.role != 'seller':
        return redirect('dashboard')

    productos = Product.objects.filter(seller=request.user)

    query = request.GET.get('q')
    stock_filter = request.GET.get('stock')

    if query:
        productos = productos.filter(name__icontains=query)

    if stock_filter == 'in':
        productos = productos.filter(stock__gt=0)
    elif stock_filter == 'out':
        productos = productos.filter(stock=0)

    return render(request, 'products/inventory.html', {'productos': productos})
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Product

@login_required
def delete_product(request, product_id):
    producto = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == 'POST':
        producto.delete()
        return redirect('inventory')  # volver al inventario

    return redirect('inventory')  # seguridad: si no es POST, igual redirecciona

@login_required
def manage_store(request):
    store, created = Store.objects.get_or_create(seller=request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StoreForm(instance=store)
    return render(request, 'products/manage_store.html', {'form': form})

# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import StoreForm
from .models import Store

@login_required
def manage_store(request):
    store, created = Store.objects.get_or_create(seller=request.user)
    
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('manage_store')  # o a una página de tienda
    else:
        form = StoreForm(instance=store)

    return render(request, 'products/manage_store.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Store, Product

User = get_user_model()

def public_store_view(request, username):
    user = get_object_or_404(User, username=username, role='seller')
    store = get_object_or_404(Store, seller=user)
    products = Product.objects.filter(seller=user)

    return render(request, 'products/public_store.html', {
        'store': store,
        'products': products
    })

from .models import Category
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})

@staff_member_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('category_list')
    return render(request, 'products/add_category.html')

@staff_member_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('category_list')

from django.http import JsonResponse
from .models import Product
from django.shortcuts import get_object_or_404

def product_detail_ajax(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    data = {
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'image': product.image.url if product.image else '',
    }
    return JsonResponse(data)

