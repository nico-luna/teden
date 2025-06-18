from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Service(models.Model):
    """Servicio que un vendedor ofrece con turno"""
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.vendor.username})"


class AvailabilitySlot(models.Model):
    """Disponibilidad recurrente por día/horario"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availability_slots')
    weekday = models.IntegerField(choices=[(i, day) for i, day in enumerate(
        ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_weekday_display()} - {self.start_time} a {self.end_time}"


class Appointment(models.Model):
    """Reserva de turno realizada por un comprador"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
        ('completed', 'Finalizado'),
        ('no_show', 'No se presentó'),
        ('rescheduled', 'Reprogramado'),
        ('expired', 'Expirado'),
        ('refunded', 'Reembolsado'),
        ('disputed', 'En disputa'),
        ('awaiting_payment', 'Esperando pago'),
        ('payment_failed', 'Pago fallido'),
        ('payment_pending', 'Pago pendiente'),
        ('payment_refunded', 'Pago reembolsado'),
        ('payment_disputed', 'Pago en disputa'),
        ('payment_confirmed', 'Pago confirmado'),
        ('payment_cancelled', 'Pago cancelado'),
        ('payment_expired', 'Pago expirado'),
        ('payment_processing', 'Procesando pago'),
        ('payment_successful', 'Pago exitoso'),
        ('payment_failed_refund', 'Reembolso de pago fallido'),
        ('payment_successful_refund', 'Reembolso de pago exitoso'),
        ('payment_pending_refund', 'Reembolso de pago pendiente'),
        ('payment_disputed_refund', 'Reembolso de pago en disputa'),
        ('payment_confirmed_refund', 'Reembolso de pago confirmado'),
        ('payment_cancelled_refund', 'Reembolso de pago cancelado'),
        ('payment_expired_refund', 'Reembolso de pago expirado'),
        ('payment_processing_refund', 'Procesando reembolso de pago'),
        ('payment_successful_refund_confirmed', 'Reembolso de pago exitoso confirmado'),        
    ]
    payment_status = models.CharField(
    max_length=20,
    choices=[('unpaid', 'No pagado'), ('paid', 'Pagado')],
    default='unpaid'
    )
    payment_id = models.CharField(max_length=100, blank=True, null=True)


    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.title} - {self.date} {self.time} ({self.status})"