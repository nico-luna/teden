from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    try:
        data = json.loads(request.body)
        print("🧠 Webhook recibido:", data)
        # Acá podrías guardar en logs o validar datos del pago con la API de MP

        # Importante: MercadoPago espera un 200 OK para no reenviar
        return JsonResponse({"status": "received"}, status=200)

    except Exception as e:
        print(f"⚠️ Error en webhook: {e}")
        return JsonResponse({"error": str(e)}, status=400)