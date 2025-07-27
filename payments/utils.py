#payments/utils.py
import requests
from plans.utils import calcular_comision_por_venta
from django.conf import settings

def crear_preferencia_para_vendedor(seller, items, buyer_email):
    perfil = seller.sellerprofile
    mp_cred = perfil.mercadopagocredential

    if not mp_cred or not mp_cred.access_token:
        raise Exception(f"El vendedor {seller} no tiene credenciales activas.")

    monto_total = sum(item["unit_price"] * item["quantity"] for item in items)
    comision = calcular_comision_por_venta(perfil, monto_total)

    preference_data = {
        "items": items,
        "payer": {"email": buyer_email},
        "back_urls": {
            "success": f"{settings.SITE_URL}/cart/checkout/mercadopago/success/",
            "failure": f"{settings.SITE_URL}/cart/checkout/mercadopago/failure/",
            "pending": f"{settings.SITE_URL}/cart/checkout/mercadopago/pending/"
        },
        "notification_url": f"{settings.SITE_URL}/cart/checkout/mercadopago/webhook/",
        "auto_return": "approved",
        "application_fee": comision
    }

    headers = {
        "Authorization": f"Bearer {mp_cred.access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.mercadopago.com/checkout/preferences", json=preference_data, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Error en la comunicación con MercadoPago: {str(e)}")

    return response.json().get("init_point")
def crear_preferencia_para_plan(vendedor, plan, buyer_email):
    mp_cred = vendedor.sellerprofile.mercadopagocredential
    if not mp_cred or not mp_cred.access_token:
        raise Exception(f"El vendedor {vendedor} no tiene credenciales activas.")

    preference_data = {
        "items": [{
            "title": f"Plan {plan.get_name_display()} en TEDEN",
            "quantity": 1,
            "unit_price": float(plan.monthly_price),
            "currency_id": "ARS"
        }],
        "payer": {"email": buyer_email},
        "back_urls": {
            "success": f"{settings.SITE_URL}/planes/confirmar-cambio/{plan.name}/",
            "failure": f"{settings.SITE_URL}/planes/fallo/",
            "pending": f"{settings.SITE_URL}/planes/pendiente/"
        },
        "auto_return": "approved"
    }

    headers = {
        "Authorization": f"Bearer {mp_cred.access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.mercadopago.com/checkout/preferences", json=preference_data, headers=headers)
        response.raise_for_status()
        return response.json().get("init_point")
    except requests.RequestException as e:
        raise Exception(f"Error en la comunicación con MercadoPago: {str(e)}")
