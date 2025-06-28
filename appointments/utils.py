from datetime import datetime, timedelta, time
from .models import Appointment

def get_available_times(service, selected_date):
    weekday = selected_date.weekday()
    duration = timedelta(minutes=service.duration_minutes)
    slots = service.availability_slots.filter(weekday=weekday)
    available_times = []

    for slot in slots:
        current_time = datetime.combine(selected_date, slot.start_time)
        end_time = datetime.combine(selected_date, slot.end_time)

        while current_time + duration <= end_time:
            # Verificar si ya hay un turno reservado
            if not Appointment.objects.filter(service=service, date=selected_date, time=current_time.time()).exists():
                available_times.append(current_time.time())
            current_time += duration

    return available_times

def get_available_dates(service, days_ahead=30):
    today = datetime.today().date()
    available_dates = []

    for offset in range(days_ahead):
        current_date = today + timedelta(days=offset)
        times = get_available_times(service, current_date)
        if times:  # si hay al menos un horario disponible
            available_dates.append(current_date)

    return available_dates