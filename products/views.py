from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models_productimage import ProductImage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm
from .models import Product, Category
from reviews.forms import ReviewForm
from django.contrib.auth import get_user_model
from orders.models import Order
import uuid
from django.contrib import messages

# Comprar producto
@login_required
@require_POST
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock > 0:
        order_number = str(uuid.uuid4())[:12]
        total_price = product.price
        order = Order.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller,
            status='pending',
            quantity=1,
            total_price=total_price,
            order_number=order_number
        )
        product.stock -= 1
        product.save()
        messages.success(request, '¡Compra realizada con éxito!')
        # Redirigir al checkout individual del producto
        return redirect('pagar_producto_individual', product_id=product.id)
    else:
        messages.error(request, 'No hay stock disponible para este producto.')
        return redirect('product_detail', product_id=product.id)
# Destacar imagen/video como cabecera
@login_required
def set_header_image(request, media_id):
    media = get_object_or_404(ProductImage, id=media_id, product__seller=request.user)
    # Desmarcar todas las demás
    ProductImage.objects.filter(product=media.product).update(is_header=False)
    media.is_header = True
    media.save()
    return redirect('edit_product', product_id=media.product.id)

# Eliminar archivo de galería
@login_required
def delete_gallery_media(request, media_id):
    media = get_object_or_404(ProductImage, id=media_id, product__seller=request.user)
    product_id = media.product.id
    media.delete()
    return redirect('edit_product', product_id=product_id)

# Mover archivo en la galería
@login_required
def move_gallery_media(request, media_id, direction):
    media = get_object_or_404(ProductImage, id=media_id, product__seller=request.user)
    product = media.product
    images = list(product.images.order_by('order'))
    idx = images.index(media)
    if direction == 'up' and idx > 0:
        prev = images[idx-1]
        media.order, prev.order = prev.order, media.order
        media.save()
        prev.save()
    elif direction == 'down' and idx < len(images)-1:
        next = images[idx+1]
        media.order, next.order = next.order, media.order
        media.save()
        next.save()
    return redirect('edit_product', product_id=product.id)
from django.db import models
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
            # Limitar cantidad de productos según el plan
            seller_profile = getattr(request.user, 'sellerprofile', None)
            plan = getattr(seller_profile, 'plan', None)
            max_products = getattr(plan, 'max_products', None)
            current_products = Product.objects.filter(seller=request.user).count()
            if max_products is not None and current_products >= max_products:
                from django.contrib import messages
                messages.error(request, f"Tu plan solo permite {max_products} productos. Actualizá tu plan para agregar más.")
                return render(request, 'products/add_product.html', {'form': form})

            product = form.save(commit=False)
            product.seller = request.user
            product.owner = request.user  # ✅ NECESARIO para evitar IntegrityError

            # Limitar productos promocionados por plan
            if getattr(product, 'is_promoted', False):
                promoted_limit = getattr(plan, 'promoted_products', None)
                current_promoted = Product.objects.filter(seller=request.user, is_promoted=True).count()
                if promoted_limit is not None and current_promoted >= promoted_limit:
                    from django.contrib import messages
            if not product.category:
                product.category = Category.get_default_category()

            product.save()
            # Guardar archivos (imágenes o videos, máx 5)
            gallery_files = request.FILES.getlist('gallery')
            from .models_productimage import ProductImage
            for i, file in enumerate(gallery_files):
                if i < 5:
                    if file.content_type.startswith('image/'):
                        ProductImage.objects.create(product=product, image=file, is_header=(i==0))
                    elif file.content_type.startswith('video/'):
                        ProductImage.objects.create(product=product, video=file, is_header=(i==0))
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

    file_size = product.file.size if product.file else None
    avg_rating = product.reviews.aggregate(models.Avg('rating')).get('rating__avg') or 0
    data = {
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'image': product.image.url if product.image else '',
        'file_size': file_size,
        'avg_rating': round(avg_rating, 1),
    }
    return JsonResponse(data)

# Vista de detalle del producto
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ReviewForm()
    orders = None
    has_completed_order = False
    header = product.images.filter(is_header=True).first()
    if request.user.is_authenticated:
        orders = product.order_set.filter(buyer=request.user, status='completed')
        has_completed_order = orders.exists()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'form': form,
        'has_completed_order': has_completed_order,
        'orders': orders,
        'header': header,
    })

from django.shortcuts import get_object_or_404, redirect
from reviews.models import Review
from django.contrib.auth.decorators import login_required

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    product_id = review.product.id
    review.delete()
    return redirect('product_detail', product_id=product_id)

# Filtrar productos en la lista general para mostrar solo los de vendedores con MercadoPago vinculado.
productos = Product.objects.filter(is_active=True, seller__sellerprofile__mercadopagocredential__isnull=False)

