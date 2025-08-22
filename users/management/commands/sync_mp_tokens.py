from django.core.management.base import BaseCommand
from users.models import User
from plans.models import SellerProfile, MercadoPagoCredential

class Command(BaseCommand):
    help = 'Sincroniza los tokens de MercadoPago de User a SellerProfile.MercadoPagoCredential'

    def handle(self, *args, **options):
        for user in User.objects.filter(role='seller'):
            if user.mercadopago_access_token:
                try:
                    perfil = SellerProfile.objects.get(user=user)
                except SellerProfile.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"No SellerProfile for user {user.username}"))
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
                    self.stdout.write(self.style.SUCCESS(f"Credencial creada para {user.username}"))
                else:
                    cred.access_token = user.mercadopago_access_token
                    cred.refresh_token = user.mercadopago_refresh_token
                    cred.user_id = user.mercadopago_user_id
                    cred.live_mode = True
                    cred.save()
                    self.stdout.write(self.style.SUCCESS(f"Credencial actualizada para {user.username}"))
