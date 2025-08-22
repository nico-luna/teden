from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order
from appointments.models import Appointment

class Command(BaseCommand):
    help = 'Cancela automáticamente órdenes y citas no pagadas después de X minutos.'

    def handle(self, *args, **options):
        # Configura el tiempo límite en minutos
        time_limit_minutes = 30
        time_limit = timezone.now() - timezone.timedelta(minutes=time_limit_minutes)

        # Cancelar órdenes pendientes
        orders = Order.objects.filter(status='pending', created_at__lt=time_limit)
        for order in orders:
            order.status = 'cancelled'
            order.save()
            self.stdout.write(self.style.WARNING(f'Orden cancelada: {order.order_number}'))

        # Cancelar citas no pagadas
        appointments = Appointment.objects.filter(payment_status='unpaid', created_at__lt=time_limit)
        for appointment in appointments:
            appointment.status = 'payment_cancelled'
            appointment.save()
            self.stdout.write(self.style.WARNING(f'Cita cancelada: {appointment.id}'))

        self.stdout.write(self.style.SUCCESS('Cancelación automática completada.'))
