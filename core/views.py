from django.shortcuts import render
from products.models import Product

def home(request):
    productos = Product.objects.exclude(id__isnull=True)  # más defensivo
    return render(request, 'core/home.html', {
        'productos': productos
    })