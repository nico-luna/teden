from plans.models import SellerPlan

# Actualizar Starter
SellerPlan.objects.filter(name='starter').update(max_products=3)

# Actualizar Plus
SellerPlan.objects.filter(name='plus').update(monthly_price=9.99, commission_percent=13)

# Actualizar Pro
SellerPlan.objects.filter(name='pro').update(monthly_price=19.99, commission_percent=7)

print('Planes actualizados correctamente.')
