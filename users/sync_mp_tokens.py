from users.models import User
from plans.models import SellerProfile, MercadoPagoCredential

def sync_mp_tokens():
    for user in User.objects.filter(role='seller'):
        if user.mercadopago_access_token:
            try:
                perfil = SellerProfile.objects.get(user=user)
            except SellerProfile.DoesNotExist:
                print(f"No SellerProfile for user {user.username}")
                continue
            cred = perfil.mercadopagocredential
            if not cred:
                cred = MercadoPagoCredential.objects.create(
                    seller_profile=perfil,
                    access_token=user.mercadopago_access_token,
                    refresh_token=user.mercadopago_refresh_token,
                    user_id=user.mercadopago_user_id,
                    live_mode=True
                )
                perfil.mercadopagocredential = cred
                perfil.save()
                print(f"Credencial creada para {user.username}")
            else:
                cred.access_token = user.mercadopago_access_token
                cred.refresh_token = user.mercadopago_refresh_token
                cred.user_id = user.mercadopago_user_id
                cred.live_mode = True
                cred.save()
                print(f"Credencial actualizada para {user.username}")

if __name__ == "__main__":
    sync_mp_tokens()
