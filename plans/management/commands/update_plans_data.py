from django.core.management.base import BaseCommand
from plans.models import SellerPlan

class Command(BaseCommand):
    help = 'Updates the SellerPlan data in the database to the values from migration 0003.'

    def handle(self, *args, **options):
        plan_defaults = {
            'starter': {
                'description': 'Plan base Starter de TEDEN',
                'monthly_price': 0.00,
                'max_products': 1,
                'max_services': 1,
                'max_stores': 1,
                'promoted_products': 0,
                'commission_percent': 20.0,
            },
            'plus': {
                'description': 'Plan Plus de TEDEN',
                'monthly_price': 9.99,
                'max_products': 20,
                'max_services': None,
                'max_stores': 3,
                'promoted_products': 1,
                'commission_percent': 13.0,
            },
            'pro': {
                'description': 'Plan Pro de TEDEN',
                'monthly_price': 19.99,
                'max_products': None,
                'max_services': None,
                'max_stores': None,
                'promoted_products': 3,
                'commission_percent': 7.0,
            },
        }

        self.stdout.write('Starting to update plans...')

        for name, defaults in plan_defaults.items():
            plan, created = SellerPlan.objects.update_or_create(
                name=name,
                defaults=defaults
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created plan "{name}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully updated plan "{name}"'))
        
        self.stdout.write(self.style.SUCCESS('All plans have been updated successfully.'))
