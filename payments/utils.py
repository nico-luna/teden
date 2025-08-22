#payments/utils.py

import requests
from plans.utils import calcular_comision_por_venta
from django.conf import settings


def _sync_mercadopago_credential(seller, token, source):
    """Sincroniza automáticamente el token en SellerProfile.MercadoPagoCredential si no existe."""
    try:
        perfil = getattr(seller, 'sellerprofile', None)
        if not perfil:
            return  # No hay perfil de vendedor

        cred = getattr(perfil, 'mercadopagocredential', None)
        if not cred:
            from plans.models import MercadoPagoCredential
            cred = MercadoPagoCredential.objects.create(
                seller_profile=perfil,
                access_token=token,
                live_mode=True  # Asumimos live_mode por defecto
            )
            perfil.mercadopagocredential = cred
            perfil.save()
        else:
            # Actualizar credencial existente si es necesario
            if cred.access_token != token:
                cred.access_token = token
                cred.live_mode = True
                cred.save()
    except Exception as e:
        print(f"Error al sincronizar credencial para {seller}: {e}")


def _get_mercadopago_token_for_seller(seller):
    """Intentar obtener un access_token de MercadoPago para el vendedor.
    Orden de búsqueda:
      1) SellerProfile.mercadopagocredential.access_token
      2) User.mercadopago_access_token
      3) Store.mercadopago_access_token (si existe store_profile)
    Retorna (token, fuente)
    """
    # 1) SellerProfile -> MercadoPagoCredential
    try:
        perfil = getattr(seller, 'sellerprofile', None)
        if perfil:
            mp_cred = getattr(perfil, 'mercadopagocredential', None) or getattr(perfil, 'mercado_cred', None)
            if mp_cred and getattr(mp_cred, 'access_token', None):
                return mp_cred.access_token, 'sellerprofile_credential'
    except Exception:
        pass

    # 2) Token directo en User
    token = getattr(seller, 'mercadopago_access_token', None)
    if token:
        _sync_mercadopago_credential(seller, token, 'user_field')
        return token, 'user_field'

    # 3) Store profile
    try:
        store = getattr(seller, 'store_profile', None)
        if store and getattr(store, 'mercadopago_access_token', None):
            _sync_mercadopago_credential(seller, store.mercadopago_access_token, 'store_profile')
            return store.mercadopago_access_token, 'store_profile'
    except Exception:
        pass

    return None, None


def crear_preferencia_para_vendedor(seller, items, buyer_email):
    """Crea una preferencia en MercadoPago usando el token del vendedor en tiempo real.

    Busca el token en varias ubicaciones y valida antes de crear la preferencia.
    Retorna el init_point (URL de checkout) en caso de éxito.
    Aplica split payment usando TEDEN_COLLECTOR_ID y application_fee.
    """
    token, fuente = _get_mercadopago_token_for_seller(seller)
    if not token:
        raise Exception(f"El vendedor {seller} no tiene credenciales activas de MercadoPago. Fuente revisada: sellerprofile | user | store.")

    from decimal import Decimal
    monto_total = sum(Decimal(str(item.get("unit_price"))) * Decimal(str(item.get("quantity"))) for item in items)

    # Calcular comisión TEDEN
    perfil = getattr(seller, 'sellerprofile', None)
    from plans.utils import calcular_comision_por_venta
    comision = calcular_comision_por_venta(perfil, monto_total) if perfil else round(monto_total * 0.2, 2)

    currency_id = getattr(settings, 'MERCADOPAGO_CURRENCY_ID', 'USD')
    items_json = []
    for item in items:
        items_json.append({
            "title": item.get("title"),
            "description": item.get("description"),
            "quantity": int(item.get("quantity", 1)),
            "unit_price": float(item.get("unit_price", 0)),
            "currency_id": currency_id
        })

    preference_data = {
        "items": items_json,
        "payer": {"email": buyer_email},
        "back_urls": {
            "success": f"{settings.SITE_URL}/cart/checkout/mercadopago/success/",
            "failure": f"{settings.SITE_URL}/cart/checkout/mercadopago/failure/",
            "pending": f"{settings.SITE_URL}/cart/checkout/mercadopago/pending/"
        },
        "notification_url": f"{settings.SITE_URL}/cart/checkout/mercadopago/webhook/",
        "auto_return": "approved",
        "marketplace": "TEDEN",
        "marketplace_fee": float(comision),
        "collector_id": settings.TEDEN_COLLECTOR_ID,
        "external_reference": f"split_{seller.id}_{buyer_email}",
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Validar token antes de crear la preferencia
        r_validate = requests.get("https://api.mercadopago.com/users/me", headers=headers)
        if r_validate.status_code != 200:
            raise Exception(f"El token del vendedor es inválido (status: {r_validate.status_code}). Pídale que reconecte su cuenta.")

        response = requests.post("https://api.mercadopago.com/checkout/preferences", json=preference_data, headers=headers)
        response.raise_for_status()
        init_point = response.json().get("init_point")
        if not init_point:
            print(f"MercadoPago error: {response.text}")
            raise Exception(f"MercadoPago no devolvió un link de pago. Respuesta: {response.text}")
    except requests.RequestException as e:
        resp = getattr(e, 'response', None)
        content = None
        try:
            if resp is not None:
                content = resp.content.decode('utf-8')
                print(f"MercadoPago error: {content}")
        except Exception:
            content = str(resp)
        raise Exception(f"Error en la comunicación con MercadoPago: {content or str(e)}")

    return init_point


def crear_preferencia_pago_plan(plan, user):
    """
    Crea una preferencia de pago en MercadoPago para la compra/cambio de un plan.
    El pago se dirige a la cuenta de la plataforma (TEDEN).
    """
    access_token = getattr(user, 'mercadopago_access_token', None)
    # Si no está en el usuario, buscar en el perfil de vendedor
    if not access_token:
        perfil = getattr(user, 'sellerprofile', None)
        if perfil:
            cred = getattr(perfil, 'mercadopagocredential', None)
            if cred and getattr(cred, 'access_token', None):
                access_token = cred.access_token
    if not access_token:
        raise Exception("El usuario no tiene un access token de MercadoPago válido. Vincula tu cuenta primero.")

    preference_data = {
        "items": [{
            "title": f"Plan {plan.name} en TEDEN",
            "description": f"Suscripción al plan {plan.name}",
            "quantity": 1,
            "unit_price": float(plan.monthly_price),
            "currency_id": "USD"
        }],
        "payer": {
            "email": user.email
        },
        "back_urls": {
            "success": f"{settings.SITE_URL}{'/mi-cuenta/'}",
            "failure": f"{settings.SITE_URL}{'/mi-cuenta/'}",
            "pending": f"{settings.SITE_URL}{'/mi-cuenta/'}"
        },
        "notification_url": f"{settings.SITE_URL}{'/payments/checkout/mercadopago/webhook/'}",
        "auto_return": "approved",
        "external_reference": f"user_{user.id}_plan_{plan.id}_{user.email}"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.mercadopago.com/checkout/preferences", json=preference_data, headers=headers)
        response.raise_for_status()
        return response.json().get("init_point")
    except requests.RequestException as e:
        resp = getattr(e, 'response', None)
        content = None
        try:
            if resp is not None:
                content = resp.content.decode('utf-8')
        except Exception:
            content = str(resp)
        # Log del error para depuración
        print(f"Error al crear preferencia de pago de plan para {user.email}: {content or str(e)}")
        raise Exception(f"Error en la comunicación con MercadoPago: {content or str(e)}")
