from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm
from .models import Product, Category
from reviews.forms import ReviewForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Agregar producto
@login_required
def add_product(request):
    if request.user.role != 'seller':
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})

# Inventario del vendedor
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

# Editar producto
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

# Eliminar producto
@login_required
def delete_product(request, product_id):
    producto = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == 'POST':
        producto.delete()
        return redirect('inventory')

    return redirect('inventory')


# Listado de categorías
@login_required
def category_list(request):
    if request.user.role != 'seller':
        return redirect('dashboard')

    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})

# Agregar categoría
@login_required
def add_category(request):
    if request.user.role != 'seller':
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('category_list')
    return render(request, 'products/add_category.html')

# Eliminar categoría
@login_required
def delete_category(request, category_id):
    if request.user.role != 'seller':
        return redirect('dashboard')

    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('category_list')

# Vista Ajax para detalles del producto
def product_detail_ajax(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    data = {
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'image': product.image.url if product.image else '',
    }
    return JsonResponse(data)

# Vista de detalle del producto
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ReviewForm()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'form': form,
    })
