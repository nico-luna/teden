from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import Product
from .forms import CheckoutForm

def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_user_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart = get_user_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = get_user_cart(request.user)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Aquí podrías crear el Order, procesar pago, enviar email, etc.
            # Por ahora vamos a vaciar el carrito y mostrar éxito:
            cart.items.all().delete()
            return render(request, 'cart/checkout_success.html', {'email': form.cleaned_data['email']})
    else:
        form = CheckoutForm()
    return render(request, 'cart/checkout.html', {'cart': cart, 'form': form})
