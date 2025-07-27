def calcular_comision_por_venta(seller_profile, monto_total):
    try:
        porcentaje = seller_profile.plan.commission_percent
        if porcentaje is None:
            raise ValueError("Porcentaje de comisión no definido.")
    except AttributeError:
        # Plan o porcentaje no definidos correctamente
        porcentaje = 20  # fallback al 20% (starter)
    except Exception:
        porcentaje = 20  # cualquier otro error

    return round(monto_total * (porcentaje / 100), 2)
