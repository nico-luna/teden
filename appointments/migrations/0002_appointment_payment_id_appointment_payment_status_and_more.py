# Generated by Django 5.2.1 on 2025-06-18 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='payment_status',
            field=models.CharField(choices=[('unpaid', 'No pagado'), ('paid', 'Pagado')], default='unpaid', max_length=20),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pendiente'), ('confirmed', 'Confirmado'), ('cancelled', 'Cancelado'), ('completed', 'Finalizado'), ('no_show', 'No se presentó'), ('rescheduled', 'Reprogramado'), ('expired', 'Expirado'), ('refunded', 'Reembolsado'), ('disputed', 'En disputa'), ('awaiting_payment', 'Esperando pago'), ('payment_failed', 'Pago fallido'), ('payment_pending', 'Pago pendiente'), ('payment_refunded', 'Pago reembolsado'), ('payment_disputed', 'Pago en disputa'), ('payment_confirmed', 'Pago confirmado'), ('payment_cancelled', 'Pago cancelado'), ('payment_expired', 'Pago expirado'), ('payment_processing', 'Procesando pago'), ('payment_successful', 'Pago exitoso'), ('payment_failed_refund', 'Reembolso de pago fallido'), ('payment_successful_refund', 'Reembolso de pago exitoso'), ('payment_pending_refund', 'Reembolso de pago pendiente'), ('payment_disputed_refund', 'Reembolso de pago en disputa'), ('payment_confirmed_refund', 'Reembolso de pago confirmado'), ('payment_cancelled_refund', 'Reembolso de pago cancelado'), ('payment_expired_refund', 'Reembolso de pago expirado'), ('payment_processing_refund', 'Procesando reembolso de pago'), ('payment_successful_refund_confirmed', 'Reembolso de pago exitoso confirmado')], default='pending', max_length=50),
        ),
    ]
