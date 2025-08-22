import time
from django.utils import timezone
from django.conf import settings
from orders.models import Order
from appointments.models import Appointment

class AutoCancelMiddleware:
    """
    Middleware que revisa y cancela órdenes/citas no pagadas cada cierto tiempo.
    Ejecuta la lógica solo si han pasado X minutos desde la última revisión.
    """
    last_run = 0
    interval_seconds = 600  # 10 minutos

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = time.time()
        if now - AutoCancelMiddleware.last_run > AutoCancelMiddleware.interval_seconds:
            self.cancel_unpaid()
            AutoCancelMiddleware.last_run = now
        response = self.get_response(request)
        return response

    def cancel_unpaid(self):
        time_limit_minutes = 30
        time_limit = timezone.now() - timezone.timedelta(minutes=time_limit_minutes)
        # Cancelar órdenes pendientes
        orders = Order.objects.filter(status='pending', created_at__lt=time_limit)
        for order in orders:
            order.status = 'cancelled'
            order.save()
        # Cancelar citas no pagadas
        appointments = Appointment.objects.filter(payment_status='unpaid', created_at__lt=time_limit)
        for appointment in appointments:
            appointment.status = 'payment_cancelled'
            appointment.save()
