# plans/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

# Esta signal se ha deshabilitado porque estaba sobreescribiendo los datos de los planes en cada reinicio.
# La creación de planes por defecto ahora es manejada por la migración 0003_seed_default_plans.py,
# que utiliza get_or_create para no alterar los datos existentes.
#
# @receiver(post_migrate)
# def create_default_plans(sender, **kwargs):
#     # Solo ejecutamos este seed cuando la app que migró es "plans"
#     if sender.name != 'plans':
#         return
#
#     SellerPlan = apps.get_model('plans', 'SellerPlan')
#     defaults = {
#         'starter': {
#             'description': 'Plan base Starter de TEDEN',
#             'monthly_price': 0.00,
#             'max_products': None,
#             'max_services': None,
#             'max_stores': None,
#             'promoted_products': 0,
#             'commission_percent': 20.0,
#         },
#         'plus': {
#             'description': 'Plan Plus de TEDEN',
#             'monthly_price': 50.00,
#             'max_products': 50,
#             'max_services': 10,
#             'max_stores': 1,
#             'promoted_products': 5,
#             'commission_percent': 15.0,
#         },
#         'pro': {
#             'description': 'Plan Pro de TEDEN',
#             'monthly_price': 100.00,
#             'max_products': None,
#             'max_services': None,
#             'max_stores': None,
#             'promoted_products': 10,
#             'commission_percent': 10.0,
#         },
#     }
#
#     for name, _ in SellerPlan.PLAN_CHOICES:
#         SellerPlan.objects.update_or_create(name=name, defaults=defaults[name])
