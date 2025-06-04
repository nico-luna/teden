from django.shortcuts import render
from products.models import Product

def home(request):
    productos = Product.objects.exclude(id__isnull=True)  # más defensivo
    return render(request, 'core/home.html', {
        'productos': productos
    })

from users.forms import CustomUserCreationForm

def home(request):
    form = CustomUserCreationForm()
    return render(request, 'core/home.html', {
        'form': form,
        'show_register_modal': False  # o True si querés que se abra automáticamente
    })