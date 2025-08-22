from django.core.management.base import BaseCommand
from plans.models import MercadoPagoCredential

class Command(BaseCommand):
    help = 'Borra todas las credenciales de MercadoPago de la base de datos'

    def handle(self, *args, **options):
        count, _ = MercadoPagoCredential.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"✔ Se eliminaron {count} credenciales de MercadoPago."))
