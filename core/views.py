from django.shortcuts import render
from products.models import Product
from users.forms import CustomUserCreationForm

def home(request):
    productos = Product.objects.filter(is_active=True)  # o .all() si querés mostrar todo
    form = CustomUserCreationForm()
    
    return render(request, 'core/home.html', {
        'productos': productos,
        'form': form,
        'show_register_modal': False
    })