from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
from users.models import User
from plans.models import SellerProfile


def _get_token_for_user(user):
    # Priorizar MercadoPagoCredential en SellerProfile
    try:
        perfil = getattr(user, 'sellerprofile', None)
        if perfil:
            mp_cred = getattr(perfil, 'mercadopagocredential', None) or getattr(perfil, 'mercado_cred', None)
            if mp_cred and getattr(mp_cred, 'access_token', None):
                return mp_cred.access_token, 'sellerprofile_credential'
    except Exception:
        pass

    # Token directo en User
    token = getattr(user, 'mercadopago_access_token', None)
    if token:
        return token, 'user_field'

    # Store profile
    try:
        store = getattr(user, 'store_profile', None)
        if store and getattr(store, 'mercadopago_access_token', None):
            return store.mercadopago_access_token, 'store_profile'
    except Exception:
        pass

    return None, None


class Command(BaseCommand):
    help = 'Verifica en tiempo real los tokens de MercadoPago de los vendedores y genera un informe JSON.'

    def handle(self, *args, **options):
        report = []
        sellers = User.objects.filter(role='seller')
        for seller in sellers:
            token, source = _get_token_for_user(seller)
            entry = {
                'username': seller.username,
                'email': seller.email,
                'token_source': source,
                'has_token': bool(token)
            }

            if not token:
                entry['valid'] = False
                entry['error'] = 'no_token_found'
                self.stdout.write(self.style.WARNING(f"{seller.username}: no token found"))
                report.append(entry)
                continue

            headers = {'Authorization': f'Bearer {token}'}
            try:
                r = requests.get('https://api.mercadopago.com/users/me', headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    entry['valid'] = True
                    entry['response'] = {
                        'id': data.get('id'),
                        'site_id': data.get('site_id'),
                        'nickname': data.get('nickname')
                    }
                    self.stdout.write(self.style.SUCCESS(f"{seller.username}: token válido (site {data.get('site_id')})"))
                else:
                    entry['valid'] = False
                    entry['error'] = f'status_{r.status_code}'
                    entry['response'] = r.text
                    self.stdout.write(self.style.ERROR(f"{seller.username}: token inválido (status {r.status_code})"))
            except Exception as e:
                entry['valid'] = False
                entry['error'] = 'request_exception'
                entry['response'] = str(e)
                self.stdout.write(self.style.ERROR(f"{seller.username}: error al verificar token: {e}"))

            report.append(entry)

        # Escribir informe al root del proyecto
        try:
            with open('mp_tokens_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS('Informe guardado en mp_tokens_report.json'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al guardar el informe: {e}'))
