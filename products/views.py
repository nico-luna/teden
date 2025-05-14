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
