# plans/migrations/0003_seed_default_plans.py
from django.db import migrations

def create_default_plans(apps, schema_editor):
    SellerPlan = apps.get_model('plans', 'SellerPlan')

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

    for name, defaults in plan_defaults.items():
        obj, created = SellerPlan.objects.get_or_create(name=name, defaults=defaults)
        # Si ya existe, no actualiza los valores

class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0002_initial'),  # ajustá si tu initial tiene otro número
    ]

    operations = [
        migrations.RunPython(create_default_plans),
    ]
