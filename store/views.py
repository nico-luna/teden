from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StorePage, StoreBlock


@login_required
def edit_store(request):
    store, _ = StorePage.objects.get_or_create(seller=request.user)
    blocks = StoreBlock.objects.filter(store=store).order_by('order')
    return render(request, 'store/manage_store.html', {
        'store': store,
        'blocks': blocks,
    })


@login_required
def add_block(request):
    if request.method == 'POST':
        block_type = request.POST.get('block_type')
        store, _ = StorePage.objects.get_or_create(seller=request.user)
        order = StoreBlock.objects.filter(store=store).count()  # Agrega al final

        StoreBlock.objects.create(
            store=store,
            block_type=block_type,
            content={},  # Inicialmente vacío
            order=order
        )
    return redirect('edit_store')


@login_required
def edit_block(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__seller=request.user)

    if request.method == 'POST':
        content = request.POST.get('content')
        block.content = {"text": content}
        block.save()
        return redirect('edit_store')

    return render(request, 'store/edit_block.html', {'block': block})


@login_required
def delete_block(request, block_id):
    block = get_object_or_404(StoreBlock, id=block_id, store__seller=request.user)
    block.delete()
    return redirect('edit_store')


def public_store(request, user_id):
    store = get_object_or_404(StorePage, seller_id=user_id)
    blocks = StoreBlock.objects.filter(store=store).order_by('order')

    return render(request, 'store/public_store.html', {
        'store': store,
        'blocks': blocks
    })