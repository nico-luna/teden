from django.core.mail import send_mail
from django.contrib import messages
# Página de contacto
def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')
        cuerpo = f"Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}"
        try:
            send_mail(
                subject=f"Nuevo mensaje de contacto de {nombre}",
                message=cuerpo,
                from_email=None,
                recipient_list=['joaco246810@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, '¡Tu mensaje fue enviado correctamente!')
        except Exception as e:
            messages.error(request, 'Hubo un error al enviar el mensaje. Intenta nuevamente.')
    return render(request, 'core/contacto.html')
from django.db import models
def ayuda(request):
    return render(request, 'core/ayuda.html')
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def run_collectstatic(request):
    call_command('collectstatic', interactive=False)
    return HttpResponse("✅ Archivos estáticos recolectados.")
from django.shortcuts import get_object_or_404
from products.models import Category
from django.shortcuts import render
def terminos(request):
    return render(request, 'core/terminos.html')
from products.models import Product
from users.forms import CustomUserCreationForm

def home(request):
    productos = Product.objects.filter(
        is_active=True,
        seller__sellerprofile__mercadopagocredential__isnull=False
    )
    form = CustomUserCreationForm(prefix='main')
    modal_form = CustomUserCreationForm(prefix='modal')
    from appointments.models import ServiceCategory
    categorias_productos = Category.objects.all()
    categorias_servicios = ServiceCategory.objects.all()
    beneficios = [
        ('variedad.png', 'Variedad de opciones', 'Encontrá todo tipo de servicios y productos digitales en un solo lugar: edición de video, diseño, música, marketing y más.'),
        ('compra.png', 'Compra y venta sencilla', 'Publicar o adquirir servicios es rápido, claro y sin complicaciones, pensado para que cualquier usuario pueda hacerlo fácil.'),
        ('reputacion.png', 'Reputación y confianza', 'Cada usuario construye su perfil con reseñas y valoraciones, lo que asegura calidad y transparencia en cada servicio.'),
        ('seguridad.png', 'Seguridad en transacciones', 'Tus compras y ventas están protegidas con sistemas de pago confiables y soporte para resolver cualquier inconveniente.'),
    ]
    return render(request, 'core/home.html', {
        'productos': productos,
        'form': form,
        'modal_form': modal_form,
        'show_register_modal': request.GET.get('register') == '1',
        'categorias_productos': categorias_productos,
        'categorias_servicios': categorias_servicios,
        'beneficios': beneficios,
    })
from cart.models import Cart
from django.http import JsonResponse
def cart_count(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = cart.items.count()
    else:
        count = 0
    return JsonResponse({'count': count})
from reviews.models import Review
def productos_por_categoria(request, category_id=None):
    productos = Product.objects.filter(is_active=True, seller__sellerprofile__mercadopagocredential__isnull=False)
    categorias = Category.objects.all()
    categoria = None
    if category_id:
        categoria = get_object_or_404(Category, id=category_id)
        productos = productos.filter(category=categoria)

    # Filtros avanzados
    tipo_archivo = request.GET.get('tipo_archivo')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    estrellas = request.GET.get('estrellas')
    min_reviews = request.GET.get('min_reviews')

    if tipo_archivo:
        productos = productos.filter(file__iendswith=tipo_archivo)
    if precio_min:
        productos = productos.filter(price__gte=precio_min)
    if precio_max:
        productos = productos.filter(price__lte=precio_max)
    if estrellas:
        productos = productos.annotate(avg_rating=models.Avg('reviews__rating')).filter(avg_rating__gte=estrellas)
    if min_reviews:
        productos = productos.annotate(num_reviews=models.Count('reviews')).filter(num_reviews__gte=min_reviews)

    return render(request, 'core/productos_por_categoria.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria': categoria,
        'selected': {
            'tipo_archivo': tipo_archivo,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'estrellas': estrellas,
            'min_reviews': min_reviews,
        }
    })
def lista_categorias(request):
    categorias = Category.objects.all()
    return render(request, 'core/lista_categorias.html', {'categorias': categorias})
def buscar_productos(request):
    q = request.GET.get('q', '').strip()
    productos = Product.objects.filter(is_active=True, seller__sellerprofile__mercadopagocredential__isnull=False)
    if q:
        productos = productos.filter(name__icontains=q)
    categorias = Category.objects.all()
    return render(request, 'core/buscar_productos.html', {
        'productos': productos,
        'q': q,
        'categorias': categorias,
    })
from django.http import JsonResponse
def buscar_productos_autocomplete(request):
    q = request.GET.get('q', '').strip()
    productos = []
    if len(q) >= 2:
        productos = list(Product.objects.filter(name__icontains=q)[:8].values('id', 'name'))
    return JsonResponse({'productos': productos})