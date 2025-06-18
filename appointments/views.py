from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ServiceForm, AvailabilitySlotForm
from .models import Service, AvailabilitySlot

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


@login_required
def set_availability(request, service_id):
    service = Service.objects.get(id=service_id, vendor=request.user)
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


from datetime import datetime
from django.contrib import messages
from .models import Appointment
from .utils import get_available_times

@login_required
def select_appointment(request, service_id):
    service = Service.objects.get(id=service_id)
    date_str = request.GET.get('date')  # formato: YYYY-MM-DD
    available_times = []
    selected_date = None

    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        available_times = get_available_times(service, selected_date)

    if request.method == 'POST':
        time_str = request.POST.get('time')
        if selected_date and time_str:
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

    return render(request, 'appointments/select_appointment.html', {
        'service': service,
        'selected_date': selected_date,
        'available_times': available_times
    })


from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def seller_appointments(request):
    appointments = Appointment.objects.filter(service__vendor=request.user).select_related('service', 'user').order_by('-date', 'time')
    
    return render(request, 'appointments/seller_dashboard.html', {
        'appointments': appointments
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

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

@login_required
def checkout_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    return render(request, 'appointments/checkout_payment.html', {
        'appointment': appointment
    })

from django.contrib.auth import get_user_model

User = get_user_model()

def ver_servicios(request):
    services = Service.objects.filter(
        is_active=True,
        vendor__ofrece_servicios=True
    ).select_related('vendor')

    return render(request, 'appointments/ver_servicios.html', {
        'services': services
    })

from django.shortcuts import get_object_or_404, render
from .models import Appointment

def pay_with_mercadopago(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    return render(request, 'appointments/pay_with_mercadopago.html', {
        'appointment': appointment
    })