# --------------------------------------
# 📦 Importaciones
# --------------------------------------
from datetime import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

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
            service = form.save(commit=False)
            service.vendor = request.user
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
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.service = service
            slot.save()
    else:
        form = AvailabilitySlotForm()

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
                    return redirect('checkout_payment', appointment_id=appointment.id)
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
    services = Service.objects.filter(
        is_active=True,
        vendor__ofrece_servicios=True
    ).select_related('vendor')

    return render(request, 'appointments/ver_servicios.html', {
        'services': services
    })


# --------------------------------------
# 🧾 Pago con MercadoPago
# --------------------------------------
@login_required
def pay_with_mercadopago(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    return render(request, 'appointments/pay_with_mercadopago.html', {
        'appointment': appointment
    })