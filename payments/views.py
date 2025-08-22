from django.http import HttpResponse

def mercadopago_oauth_callback(request):
    # Procesa el callback de MercadoPago
    code = request.GET.get('code')
    error = request.GET.get('error')
    if error:
        return HttpResponse(f"Error en la autorización: {error}")
    if not code:
        return HttpResponse("No se recibió el código de autorización.")

    # Intercambiar el code por el access_token
    import requests
    import json
    from django.conf import settings
    token_url = "https://api.mercadopago.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.MP_CLIENT_ID,
        "client_secret": settings.MP_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.MP_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        user_id = data.get("user_id")
        from django.utils import timezone
        from store.models import Store
        if request.user.is_authenticated:
            store, _ = Store.objects.get_or_create(
                owner=request.user,
                defaults={'name': f"Tienda de {request.user.username}"}
            )
            store.mercadopago_connected = True
            store.mercadopago_user_id = user_id
            store.mercadopago_access_token = access_token
            store.mercadopago_refresh_token = refresh_token
            store.mercadopago_last_sync = timezone.now()
            store.save()
            from django.contrib import messages
            messages.success(request, "✅ Tu cuenta de MercadoPago fue conectada con éxito.")
            from django.shortcuts import redirect
            return redirect("dashboard")
        else:
            return HttpResponse(f"¡Cuenta conectada! Access token: {access_token}")
    else:
        return HttpResponse(f"Error al obtener access_token: {response.text}")
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import requests
from django.conf import settings


@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    try:
        # 1. ✅ Validar clave secreta del Webhook
        SECRET_KEY = settings.MP_WEBHOOK_SECRET
        received_secret = request.headers.get('X-Webhook-Secret')

        if received_secret != SECRET_KEY:
            print("❌ Clave secreta inválida en Webhook.")
            return JsonResponse({'error': 'Invalid secret'}, status=403)

        # 2. 📦 Parsear datos recibidos
        data = json.loads(request.body)
        print("📩 Webhook recibido:", data)

        topic = data.get("type") or data.get("topic")
        payment_id = data.get("data", {}).get("id")

        if topic == "payment" and payment_id:
            # 3. 📡 Consultar pago en la API de MP
            access_token = settings.MERCADOPAGO_ACCESS_TOKEN  # Token global del sistema
            url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                payment_info = response.json()
                status = payment_info.get("status")
                print(f"💰 Pago {payment_id} tiene estado: {status}")

                if status == "approved":
                    # Procesar el pago de plan: buscar el usuario y el plan, actualizar SellerProfile
                    additional_info = payment_info.get("additional_info", {})
                    items = additional_info.get("items", [])
                    if items:
                        item_title = items[0].get("title", "")
                        # Ejemplo: "Plan TEDEN Plus en TEDEN"
                        if "Plan" in item_title:
                            import re
                            match = re.search(r"Plan (TEDEN [^ ]+)", item_title)
                            if match:
                                plan_name = match.group(1).lower().replace("teden ", "")
                                from plans.models import SellerPlan, SellerProfile
                                from django.contrib.auth import get_user_model
                                User = get_user_model()
                                payer_email = payment_info.get("payer", {}).get("email")
                                try:
                                    user = User.objects.get(email=payer_email)
                                    plan = SellerPlan.objects.get(name=plan_name)
                                    profile = SellerProfile.objects.get(user=user)
                                    profile.plan = plan
                                    profile.save()
                                    # Marcar usuario como verificado si el plan es plus o pro
                                    if plan.name in ["plus", "pro"]:
                                        user.is_verified = True
                                        user.save()
                                    print(f"✅ Plan actualizado a {plan_name} para {user.email} (verificado: {user.is_verified})")
                                except Exception as e:
                                    print(f"❌ Error actualizando plan: {e}")
                    print("✅ Procesar el pedido como pagado")

                return JsonResponse({"status": "processed"}, status=200)
            else:
                print("❌ No se pudo verificar el pago con la API de MP")
                return JsonResponse({"error": "Payment verification failed"}, status=400)

        print("⚠️ Evento no manejado o sin ID de pago")
        return JsonResponse({"status": "ignored"}, status=200)

    except Exception as e:
        print(f"⚠️ Error procesando webhook: {e}")
        return JsonResponse({"error": str(e)}, status=400)
