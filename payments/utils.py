# payments/utils.py
import requests
from plans.utils import calcular_comision_por_venta

def crear_preferencia_para_vendedor(seller, items, buyer_email):
    perfil = seller.sellerprofile
    mp_cred = perfil.mercadopagocredential

    if not mp_cred:
        raise Exception(f"El vendedor {seller} no tiene MercadoPago conectado.")

    monto_total = sum(item["unit_price"] * item["quantity"] for item in items)
    comision = calcular_comision_por_venta(perfil, monto_total)

    preference_data = {
        "items": items,
        "payer": {"email": buyer_email},
        "back_urls": {
            "success": "https://teden.com/cart/checkout/mercadopago/success/",
            "failure": "https://teden.com/cart/checkout/mercadopago/failure/",
            "pending": "https://teden.com/cart/checkout/mercadopago/pending/"
        },
        "auto_return": "approved",
        "application_fee": comision
    }

    headers = {
        "Authorization": f"Bearer {mp_cred.access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.mercadopago.com/checkout/preferences", json=preference_data, headers=headers)
    
    if response.status_code != 201:
        raise Exception(f"Error al crear preferencia: {response.text}")

    return response.json().get("init_point")
