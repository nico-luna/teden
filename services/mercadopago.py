import os
import mercadopago

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

def crear_preferencia(items, email):
    preference_data = {
        "items": [
            {
                "title": item["title"],
                "quantity": item["quantity"],
                "currency_id": "ARS",
                "unit_price": float(item["unit_price"]),
            } for item in items
        ],
        "payer": {"email": email},
        "back_urls": {
            "success": "https://teden.com/success",
            "failure": "https://teden.com/failure",
            "pending": "https://teden.com/pending",
        },
        "auto_return": "approved",
    }
    preference_response = sdk.preference().create(preference_data)
    return preference_response["response"]["id"]