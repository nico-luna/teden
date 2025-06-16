from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .models import Store, StoreBlock
from .utils import load_default_blocks
from .forms import StoreCreateForm


# Función auxiliar para generar slugs únicos
def generar_slug_unico(nombre_base):
    base = slugify(nombre_base)
    slug = base
    contador = 1
    while Store.objects.filter(slug=slug).exists():
        slug = f"{base}-{contador}"
        contador += 1
    return slug


# Vista para crear tienda
@login_required
def crear_tienda(request):
    if request.method == 'POST':
        form = StoreCreateForm(request.POST)
        if form.is_valid():
            nombre_tienda = form.cleaned_data['name']
            slug_unico = generar_slug_unico(nombre_tienda)

            store = Store.objects.create(
                owner=request.user,
                name=nombre_tienda,
                slug=slug_unico
            )

            for i, block in enumerate(load_default_blocks()):
                StoreBlock.objects.create(
                    store=store,
                    block_type=block["type"],
                    content=block["props"],
                    order=i
                )

            return redirect('edit_store')
    else:
        form = StoreCreateForm()

    return render(request, 'store/crear_tienda.html', {'form': form})


# Vista para editar bloques de la tienda
@login_required
def edit_store(request):
    store = get_object_or_404(Store, owner=request.user)
    blocks = StoreBlock.objects.filter(store=store).order_by('order')
    return render(request, 'store/manage_store.html', {
        'store': store,
        'blocks': blocks,
    })


# Agregar bloque
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


# Editar bloque
@login_required
def edit_block(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)

    if request.method == 'POST':
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


# Eliminar bloque
@login_required
def delete_block(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)
    block.delete()
    return redirect('edit_store')


# Vista pública de la tienda
def public_store(request, slug):
    store = get_object_or_404(Store, slug=slug)
    blocks = StoreBlock.objects.filter(store=store).order_by('order')
    return render(request, 'store/public_store.html', {
        'store': store,
        'blocks': blocks
    })
