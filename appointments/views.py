# Vista para filtrar servicios por categoría
def servicios_por_categoria(request, categoria_id):
    from .models import Service, ServiceCategory
    servicios = Service.objects.filter(is_active=True, category_id=categoria_id, vendor__sellerprofile__mercadopagocredential__isnull=False)
    categoria = ServiceCategory.objects.get(id=categoria_id)
    categorias = ServiceCategory.objects.all()
    return render(request, 'appointments/servicios_por_categoria.html', {
        'servicios': servicios,
        'categoria': categoria,
        'categorias': categorias,
    })
# --------------------------------------
# 📦 Importaciones
# --------------------------------------
from datetime import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from appointments.models import ServiceCategory
from reviews.models import Review
from django.db import models
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.forms import modelformset_factory

from .forms import ServiceForm, AvailabilitySlotForm
from .models import Service, AvailabilitySlot, Appointment
from .utils import get_available_times, get_available_dates

User = get_user_model()

# --------------------------------------
# 🛠️ Crear servicio (solo vendedores)
# --------------------------------------
@login_required
def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            # Limitar servicios por plan
            user = request.user
            seller_profile = getattr(user, 'sellerprofile', None)
            if seller_profile and seller_profile.plan:
                max_services = seller_profile.plan.max_services
                current_services = user.services.count()
                if max_services is not None and current_services >= max_services:
                    messages.error(request, f"Has alcanzado el límite de servicios permitidos por tu plan ({max_services}).")
                    return render(request, 'appointments/create_service.html', {'form': form})
            service = form.save(commit=False)
            service.vendor = user
            service.save()
            return redirect('set_availability', service_id=service.id)
    else:
        form = ServiceForm()
    return render(request, 'appointments/create_service.html', {'form': form})


# --------------------------------------
# 📆 Definir disponibilidad para el servicio
# --------------------------------------
@login_required
def set_availability(request, service_id):
    service = get_object_or_404(Service, id=service_id, vendor=request.user)

    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST, duracion=service.duration_minutes)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.service = service
            slot.save()
    else:
        form = AvailabilitySlotForm(duracion=service.duration_minutes)

    slots = service.availability_slots.all()

    return render(request, 'appointments/set_availability.html', {
        'form': form,
        'service': service,
        'slots': slots
    })


# --------------------------------------
# 📅 Seleccionar turno para reservar (comprador)
# --------------------------------------
@login_required
def select_appointment(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    date_str = request.GET.get('date')  # formato: YYYY-MM-DD
    
    selected_date = None
    available_times = []
    available_dates = [d.isoformat() for d in get_available_dates(service)]

    # Buscar horarios si hay fecha seleccionada
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            available_times = get_available_times(service, selected_date)
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")

    # Confirmar reserva si se elige un horario
    if request.method == 'POST':
        time_str = request.POST.get('time')
        if selected_date and time_str:
            try:
                time_obj = datetime.strptime(time_str, "%H:%M").time()
                if Appointment.objects.filter(service=service, date=selected_date, time=time_obj).exists():
                    messages.error(request, "Ese horario ya fue reservado.")
                else:
                    appointment = Appointment.objects.create(
                        service=service,
                        user=request.user,
                        date=selected_date,
                        time=time_obj,
                        status='pending',
                        payment_status='unpaid'
                    )
                    messages.success(request, "¡Turno reservado con éxito!")
                    return redirect('appointments_checkout_payment', appointment_id=appointment.id)
            except ValueError:
                messages.error(request, "Hora inválida.")

    return render(request, 'appointments/select_appointment.html', {
        'service': service,
        'selected_date': selected_date,
        'available_times': available_times,
            'available_dates': json.dumps(available_dates)
    })


# --------------------------------------
# 📋 Ver turnos como vendedor
# --------------------------------------
@login_required
def seller_appointments(request):
    appointments = Appointment.objects.filter(
        service__vendor=request.user
    ).select_related('service', 'user').order_by('-date', 'time')

    return render(request, 'appointments/seller_dashboard.html', {
        'appointments': appointments
    })


# --------------------------------------
# 🔄 Cambiar estado de una reserva
# --------------------------------------
@login_required
def change_appointment_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, id=appointment_id, service__vendor=request.user)

    if new_status in ['pending', 'confirmed', 'cancelled', 'completed']:
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Turno actualizado a: {appointment.get_status_display()}")
    else:
        messages.error(request, "Estado no válido.")

    return redirect('seller_appointments')


# --------------------------------------
# 💳 Checkout de pago (vinculado a la reserva)
# --------------------------------------
@login_required
def checkout_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    return render(request, 'appointments/checkout_payment.html', {
        'appointment': appointment
    })


# --------------------------------------
# 🧭 Explorar servicios activos disponibles
# --------------------------------------
def ver_servicios(request):
    services = Service.objects.filter(is_active=True, vendor__ofrece_servicios=True, vendor__sellerprofile__mercadopagocredential__isnull=False).select_related('vendor', 'category')
    categorias = ServiceCategory.objects.all()
    categoria_id = request.GET.get('categoria_id')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    estrellas = request.GET.get('estrellas')
    min_reviews = request.GET.get('min_reviews')

    if categoria_id:
        services = services.filter(category_id=categoria_id)
    if precio_min:
        services = services.filter(price__gte=precio_min)
    if precio_max:
        services = services.filter(price__lte=precio_max)
    if estrellas:
        services = services.annotate(avg_rating=Avg('reviews__rating', filter=models.Q(reviews__isnull=False))).filter(avg_rating__gte=estrellas)
    if min_reviews:
        services = services.annotate(num_reviews=Count('reviews', filter=models.Q(reviews__isnull=False))).filter(num_reviews__gte=min_reviews)

    return render(request, 'appointments/ver_servicios.html', {
        'services': services,
        'categorias': categorias,
        'selected': {
            'categoria_id': categoria_id,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'estrellas': estrellas,
            'min_reviews': min_reviews,
        }
    })


# --------------------------------------
# 🧾 Pago con MercadoPago
# --------------------------------------
@login_required
def pay_with_mercadopago(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    # Generar preferencia de MercadoPago
    from payments.utils import crear_preferencia_para_vendedor
    seller = appointment.service.vendor
    items = [{
        "title": appointment.service.title,
        "quantity": 1,
        "unit_price": float(appointment.service.price),
        "currency_id": "ARS"
    }]

    mercadopago_url = crear_preferencia_para_vendedor(
        seller=seller,
        items=items,
        buyer_email=request.user.email
    )
    if mercadopago_url:
        return redirect(mercadopago_url)
    return render(request, 'appointments/pay_with_mercadopago.html', {
        'appointment': appointment,
        'mercadopago_url': mercadopago_url
    })


# --------------------------------------
# 🔍 Buscar servicios
# --------------------------------------
def buscar_servicios(request):
    q = request.GET.get('q', '').strip()
    servicios = Service.objects.all()
    if q:
        servicios = servicios.filter(name__icontains=q)
    context = {
        'servicios': servicios,
        'q': q,
    }
    return render(request, 'appointments/buscar_servicios.html', context)

def buscar_servicios_autocomplete(request):
    q = request.GET.get('q', '').strip()
    servicios = []
    if len(q) >= 2:
        servicios = list(Service.objects.filter(name__icontains=q)[:8].values('id', 'name'))
    return JsonResponse({'servicios': servicios})

# --------------------------------------
# ✏️ Editar servicio (solo vendedores)
# --------------------------------------
@login_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id, vendor=request.user)
    ServiceFormSet = modelformset_factory(AvailabilitySlot, form=AvailabilitySlotForm, extra=0, can_delete=True)

    if request.method == 'POST':
        service_form = ServiceForm(request.POST, instance=service)
        slots_formset = ServiceFormSet(request.POST, queryset=service.availability_slots.all())
        if service_form.is_valid() and slots_formset.is_valid():
            service_form.save()
            slots_formset.save()
            return redirect('dashboard_seller')
    else:
        service_form = ServiceForm(instance=service)
        slots_formset = ServiceFormSet(queryset=service.availability_slots.all())

    return render(request, 'appointments/edit_service.html', {
        'service_form': service_form,
        'slots_formset': slots_formset,
        'service': service,
    })