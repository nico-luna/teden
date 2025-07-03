def calcular_comision_por_venta(seller_profile, monto_total):
    porcentaje = seller_profile.plan.commission_percent
    return round(monto_total * (porcentaje / 100), 2)