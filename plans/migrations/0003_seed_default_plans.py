# plans/migrations/0003_seed_default_plans.py
from django.db import migrations

def create_default_plans(apps, schema_editor):
    SellerPlan = apps.get_model('plans', 'SellerPlan')

    plan_defaults = {
        'starter': {
            'description': 'Plan base Starter de TEDEN',
            'monthly_price': 0.00,
            'max_products': None,
            'max_services': None,
            'max_stores': None,
            'promoted_products': 0,
            'commission_percent': 20.0,
        },
        'plus': {
            'description': 'Plan Plus de TEDEN',
            'monthly_price': 50.00,
            'max_products': 50,
            'max_services': 10,
            'max_stores': 1,
            'promoted_products': 5,
            'commission_percent': 15.0,
        },
        'pro': {
            'description': 'Plan Pro de TEDEN',
            'monthly_price': 100.00,
            'max_products': None,
            'max_services': None,
            'max_stores': None,
            'promoted_products': 10,
            'commission_percent': 10.0,
        },
    }

    for name, defaults in plan_defaults.items():
        SellerPlan.objects.update_or_create(
            name=name,
            defaults=defaults
        )

class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0002_initial'),  # ajustá si tu initial tiene otro número
    ]

    operations = [
        migrations.RunPython(create_default_plans),
    ]
