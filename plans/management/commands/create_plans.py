from django.core.management.base import BaseCommand
from plans.models import SellerPlan

class Command(BaseCommand):
    help = 'Crea los planes iniciales de TEDEN'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'starter',
                'description': 'Ideal para quienes están comenzando en el mundo digital.',
                'monthly_price': 0.00,
                'max_products': 3,
                'max_services': 1,
                'max_stores': 1,
                'promoted_products': 0,
                'commission_percent': 20.0,
            },
            {
                'name': 'plus',
                'description': 'Para creadores activos que quieren mayor visibilidad.',
                'monthly_price': 9.99,
                'max_products': 20,
                'max_services': None,
                'max_stores': 3,
                'promoted_products': 1,
                'commission_percent': 13.0,
            },
            {
                'name': 'pro',
                'description': 'Pensado para profesionales o agencias.',
                'monthly_price': 20.00,
                'max_products': None,
                'max_services': None,
                'max_stores': None,
                'promoted_products': 3,
                'commission_percent': 7.0,
            }
        ]

        for plan in plans:
            SellerPlan.objects.update_or_create(name=plan['name'], defaults=plan)

        self.stdout.write(self.style.SUCCESS("✔ Planes TEDEN creados correctamente"))
