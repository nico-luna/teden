from django.core.management.base import BaseCommand
from plans.models import SellerPlan

class Command(BaseCommand):
    help = 'Shows the current SellerPlan data from the database.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching current plan data from the database...')
        plans = SellerPlan.objects.all().order_by('monthly_price')
        if not plans:
            self.stdout.write(self.style.WARNING('No plans found in the database.'))
            return

        for plan in plans:
            self.stdout.write(self.style.SUCCESS(f'--- Plan: {plan.name} ---'))
            self.stdout.write(f"  Description: {plan.description}")
            self.stdout.write(f"  Monthly Price: {plan.monthly_price}")
            self.stdout.write(f"  Max Products: {plan.max_products}")
            self.stdout.write(f"  Max Services: {plan.max_services}")
            self.stdout.write(f"  Max Stores: {plan.max_stores}")
            self.stdout.write(f"  Promoted Products: {plan.promoted_products}")
            self.stdout.write(f"  Commission Percent: {plan.commission_percent}")
            self.stdout.write('\n')