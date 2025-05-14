from django.shortcuts import render
from products.models import Product

def home(request):
    productos = Product.objects.all()
    return render(request, 'core/home.html', {'productos': productos})


