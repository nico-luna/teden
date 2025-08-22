# views.py (fragmento central mejorado para personalización total)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils.text import slugify
from .models import Store, StoreBlock
from .forms.blocks import BLOCK_FORM_MAP
from .forms_store import StoreCreateForm, StoreEditForm
from .utils import load_default_blocks
import json

# Utils

def generar_slug_unico(nombre_base):
    base = slugify(nombre_base)
    slug = base
    contador = 1
    while Store.objects.filter(slug=slug).exists():
        slug = f"{base}-{contador}"
        contador += 1
    return slug

# Crear tienda
@login_required
def crear_tienda(request):
    if request.method == 'POST':
        form = StoreCreateForm(request.POST)
        if form.is_valid():
            # Limitar tiendas por plan
            user = request.user
            seller_profile = getattr(user, 'sellerprofile', None)
            if seller_profile and seller_profile.plan:
                max_stores = seller_profile.plan.max_stores
                current_stores = Store.objects.filter(owner=user).count()
                if max_stores is not None and current_stores >= max_stores:
                    from django.contrib import messages
                    messages.error(request, f"Has alcanzado el límite de tiendas permitidas por tu plan ({max_stores}).")
                    return render(request, 'store/crear_tienda.html', {'form': form})
            nombre_tienda = form.cleaned_data['name']
            slug_unico = generar_slug_unico(nombre_tienda)
            store = Store.objects.create(owner=user, name=nombre_tienda, slug=slug_unico)
            for i, block in enumerate(load_default_blocks()):
                StoreBlock.objects.create(
                    store=store,
                    block_type=block["type"],
                    content=block["props"],
                    order=i
                )
            return redirect('store:edit_store')
    else:
        form = StoreCreateForm()
    return render(request, 'store/crear_tienda.html', {'form': form})

# Editar tienda
@login_required
def edit_store(request):
    store = request.user.store_profile
    if request.method == 'POST':
        form = StoreEditForm(request.POST, request.FILES, instance=store)
        # Actualizar el estado de la tienda según el checkbox
        is_active = request.POST.get('is_active') == 'true' or request.POST.get('is_active') == 'on'
        form.instance.is_active = is_active
        if form.is_valid():
            form.save()
            return redirect('store:edit_store')
    else:
        form = StoreEditForm(instance=store)

    public_url = request.build_absolute_uri(reverse('store:public_store', args=[store.slug]))
    blocks = store.blocks.order_by('order')
    block_forms = [
        (block, BLOCK_FORM_MAP[block.block_type](initial=block.content))
        if BLOCK_FORM_MAP.get(block.block_type)
        else (block, None)
        for block in blocks
    ]

    return render(request, 'store/mi_tienda.html', {
        'form': form,
        'store': store,
        'public_url': public_url,
        'block_forms': block_forms
    })

# Editar contenido de bloque (AJAX)
@login_required
@require_POST
def update_block_content(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)
    form_class = BLOCK_FORM_MAP.get(block.block_type)
    if not form_class:
        return JsonResponse({'error': 'Bloque no soportado'}, status=400)

    form = form_class(request.POST)
    if form.is_valid():
        block.content = form.cleaned_data
        block.save()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'errors': form.errors}, status=400)

# Agregar bloque
@login_required
@require_POST
def add_block(request):
    block_type = request.POST.get('block_type')
    store = request.user.store_profile
    order = store.blocks.count()
    block = StoreBlock.objects.create(store=store, block_type=block_type, content={}, order=order)
    messages.success(request, 'Bloque agregado correctamente.')
    return redirect('store:edit_store')

# Duplicar bloque
@login_required
@require_POST
def duplicate_block(request, block_id):
    original = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)
    StoreBlock.objects.create(
        store=original.store,
        block_type=original.block_type,
        content=original.content,
        order=original.order + 1
    )
    return redirect('store:edit_store')

# Eliminar bloque
@login_required
@require_POST
def delete_block(request, block_id):
    try:
        block = StoreBlock.objects.get(id=block_id, store__owner=request.user)
        block.delete()
        return redirect('store:edit_store')
    except StoreBlock.DoesNotExist:
        messages.error(request, 'El bloque no existe o no tienes permisos para eliminarlo.')
        return redirect('store:edit_store')

# Cambiar orden de bloques
@login_required
@require_POST
def update_block_order(request):
    try:
        data = json.loads(request.body)
        order = data.get('order', [])
        for index, block_id in enumerate(order):
            StoreBlock.objects.filter(id=block_id, store__owner=request.user).update(order=index)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Activar/desactivar bloque
@login_required
@require_POST
def toggle_block_visibility(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)
    block.visible = not block.visible
    block.save()
    return JsonResponse({'status': 'ok', 'visible': block.visible})

# Vista pública
import json

def public_store(request, slug):
    store = get_object_or_404(Store, slug=slug)
    blocks = store.blocks.filter(visible=True).order_by('order')  

    parsed_blocks = []
    for block in blocks:
        content = block.content
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                content = {}
        parsed_blocks.append({
            'type': block.block_type,
            'content': content
        })

    return render(request, 'store/public_store.html', {
        'store': store,
        'blocks': parsed_blocks
    })

#edit_block

from store.forms.blocks import BLOCK_FORM_MAP
from django.core.files.storage import default_storage
@login_required
def edit_block(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__owner=request.user)
    FormClass = BLOCK_FORM_MAP.get(block.block_type)

    if not FormClass:
        return render(request, 'store/edit_block.html', {
            'block': block,
            'error': f"No hay un formulario definido para el tipo de bloque '{block.block_type}'"
        })

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data
            # Guardar imagen de fondo para Hero
            if 'background_image' in request.FILES:
                from django.core.files.base import ContentFile
                image = request.FILES['background_image']
                filename = default_storage.save(f'store_blocks/{image.name}', ContentFile(image.read()))
                url = default_storage.url(filename)
                print('URL de imagen hero:', url)
                content['background_image'] = url
            # Guardar imagen para About
            if 'image' in request.FILES:
                from django.core.files.base import ContentFile
                image = request.FILES['image']
                filename = default_storage.save(f'store_blocks/{image.name}', ContentFile(image.read()))
                content['image'] = default_storage.url(filename)
            block.content = content
            block.save()
            return redirect('store:edit_store')
    else:
        form = FormClass(initial=block.content)

    return render(request, 'store/edit_block.html', {
        'form': form,
        'block': block
    })
