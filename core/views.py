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

from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def run_collectstatic(request):
    call_command('collectstatic', interactive=False)
    return HttpResponse("✅ Archivos estáticos recolectados.")

from appointments.models import Service

def home(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'core/home.html', {'services': services})

from django.shortcuts import render

def ayuda(request):
    return render(request, 'core/ayuda.html')


def terminos(request):
    return render(request, 'core/terminos.html')