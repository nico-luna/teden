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
                    # Acá podés procesar la orden, marcarla como pagada, etc.
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
