from celery import shared_task
from django.utils import timezone
from orders.models import Order
from appointments.models import Appointment

@shared_task
def cancel_unpaid_task():
    time_limit_minutes = 30
    time_limit = timezone.now() - timezone.timedelta(minutes=time_limit_minutes)

    orders = Order.objects.filter(status='pending', created_at__lt=time_limit)
    for order in orders:
        order.status = 'cancelled'
        order.save()

    appointments = Appointment.objects.filter(payment_status='unpaid', created_at__lt=time_limit)
    for appointment in appointments:
        appointment.status = 'payment_cancelled'
        appointment.save()

    return f"Cancelación automática completada: {orders.count()} órdenes, {appointments.count()} citas."
