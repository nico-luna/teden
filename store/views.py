from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Store, StoreBlock
from .utils import load_default_blocks
from products.models import Product, Category  # ajustá imports si usás otra app

@login_required
def dashboard(request):
    if request.user.role == 'buyer':
        return render(request, 'users/dashboard_buyer.html')

    elif request.user.role == 'seller':
        from store.models import Store
        store = Store.objects.filter(owner=request.user).first()
        public_url = reverse('public_store', args=[store.slug]) if store else None

        product_count = Product.objects.filter(seller=request.user).count()
        category_count = Category.objects.filter(seller=request.user).count()  # ajustá si es global

        context = {
            'store': store,
            'public_url': public_url,
            'product_count': product_count,
            'category_count': category_count,
        }
        return render(request, 'users/dashboard_seller.html', context)

    else:
        return redirect('select_role')

@login_required
def edit_store(request):
    store, _ = Store.objects.get_or_create(owner=request.user)
    blocks = StoreBlock.objects.filter(store=store).order_by('order')
    return render(request, 'store/manage_store.html', {
        'store': store,
        'blocks': blocks,
    })

@login_required
def add_block(request):
    if request.method == 'POST':
        block_type = request.POST.get('block_type')
        store, _ = Store.objects.get_or_create(owner=request.user)
        order = StoreBlock.objects.filter(store=store).count()
        StoreBlock.objects.create(
            store=store,
            block_type=block_type,
            content={},
            order=order
        )
    return redirect('edit_store')

@login_required
def edit_block(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)

    if request.method == 'POST':
        # Solo para tipo hero por ahora
        if block.block_type == 'hero':
            block.content = {
                "title": request.POST.get('title', ''),
                "subtitle": request.POST.get('subtitle', ''),
                "background_image": request.POST.get('background_image', ''),
                "text_color": request.POST.get('text_color', '#000000')
            }
            block.save()
        return redirect('edit_store')

    return render(request, 'store/edit_block.html', {'block': block})


@login_required
def delete_block(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)
    block.delete()
    return redirect('edit_store')

def public_store(request, slug):
    store = get_object_or_404(Store, slug=slug)
    blocks = StoreBlock.objects.filter(store=store).order_by('order')
    return render(request, 'store/public_store.html', {
        'store': store,
        'blocks': blocks
    })

@login_required
def crear_tienda(request):
    if request.method == 'POST':
        store = Store.objects.create(owner=request.user, name="Mi Tienda")
        for i, block in enumerate(load_default_blocks()):
            StoreBlock.objects.create(
                store=store,
                block_type=block["type"],
                content=block["props"],
                order=i
            )
        return redirect('edit_store')
    return render(request, 'store/crear_tienda.html')

def public_store(request, slug):
    store = get_object_or_404(Store, slug=slug)
    blocks = StoreBlock.objects.filter(store=store).order_by('order')
    return render(request, 'store/public_store.html', {
        'store': store,
        'blocks': blocks
    })
