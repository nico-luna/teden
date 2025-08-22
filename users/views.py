# Vista de login manual


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('/')
    return render(request, 'users/login.html', {'form': form})
import requests
from django.utils import timezone
from .models import GoogleCredential

def google_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    if not code or not state or state != request.session.get("oauth_state"):
        return HttpResponse("Error de autenticación.", status=400)

    # Intercambiar el código por tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code",
    }
    token_resp = requests.post(token_url, data=data)
    if token_resp.status_code != 200:
        return HttpResponse("Error al obtener el token.", status=400)
    token_data = token_resp.json()

    # Obtener datos del usuario
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    userinfo_resp = requests.get(userinfo_url, headers=headers)
    if userinfo_resp.status_code != 200:
        return HttpResponse("Error al obtener datos del usuario.", status=400)
    userinfo = userinfo_resp.json()

    # Autenticar/crear usuario en Django
    from django.contrib.auth import get_user_model, login
    User = get_user_model()
    user, _ = User.objects.get_or_create(email=userinfo["email"], defaults={"username": userinfo["email"].split("@")[0]})
    login(request, user)

    # Guardar credenciales asociadas al usuario
    expires_at = timezone.now() + timezone.timedelta(seconds=token_data.get("expires_in", 3600))
    cred, created = GoogleCredential.objects.update_or_create(
        sub=userinfo["sub"],
        defaults={
            "user": user,
            "email": userinfo["email"],
            "picture": userinfo.get("picture"),
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": expires_at,
            "raw": token_data,
        },
    )
    return redirect("/")
import os, secrets, urllib.parse
from django.shortcuts import redirect

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

def google_login(request):
    request.session["oauth_state"] = secrets.token_urlsafe(24)

    params = {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",          # para obtener refresh_token
        "prompt": "consent",               # fuerza refresh_token la 1ª vez
        "state": request.session["oauth_state"],
        # "include_granted_scopes": "true", # opcional
    }
    return redirect(f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}")
from django.http import HttpResponse
from plans.models import SellerProfile, MercadoPagoCredential

def borrar_cuentas_mercadopago(request):
    MercadoPagoCredential.objects.all().delete()
    return HttpResponse("Todas las cuentas de MercadoPago han sido borradas.")
# views.py

import random
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_protect  # 👈 acá sí
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt

from plans.models import MercadoPagoCredential, SellerPlan, SellerProfile
from store.models import Store
from .forms import (
    CustomUserCreationForm,
    EditProfileForm,
    SellerRegistrationForm,
    VerificationCodeForm,
)
from .models import EmailVerificationCode

User = get_user_model()

# ─────────────────────────────────────────────────────────────
# REGISTRO
# ─────────────────────────────────────────────────────────────
@csrf_protect
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # 1️⃣ Crear usuario
                user = form.save(commit=False)
                user.role = "buyer"
                user.save()

                # 2️⃣ Generar / guardar código y marcar como NO verificado
                code = str(random.randint(100_000, 999_999))
                EmailVerificationCode.objects.update_or_create(
                    user=user, defaults={"code": code, "verified": False}
                )

                # 3️⃣ Enviar e-mail
                subject = "Verificá tu cuenta en TEDEN"
                text_content = (
                    f"Hola {user.get_full_name() or user.username},\n\n"
                    f"Tu código de verificación es: {code}\n\n"
                    "Si no solicitaste este correo, podés ignorarlo."
                )
                html_content = render_to_string(
                    "users/emails/verification_email.html",
                    {"user": user, "code": code, "current_year": timezone.now().year},
                )
                msg = EmailMultiAlternatives(
                    subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # 4️⃣ Autenticar e iniciar sesión
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                # 5️⃣ Redirigir a verificación
                messages.info(
                    request,
                    "Te enviamos un código a tu correo. Verificalo para continuar.",
                )
                return redirect("verify_email")
            except IntegrityError:
                messages.error(
                    request, "Este nombre de usuario o email ya está registrado."
                )
        else:
            messages.error(request, "Revisá los campos del formulario.")
        return render(
            request,
            "users/register.html",
            {"form": form},
        )

    # GET
    form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})



# ─────────────────────────────────────────────────────────────
# CONVERTIRSE EN VENDEDOR
# ─────────────────────────────────────────────────────────────
@login_required
def convertirse_en_vendedor(request):
    user = request.user

    if user.role == "seller":
        # Si ya es vendedor, asegurar que tiene plan Starter
        starter_plan, _ = SellerPlan.objects.get_or_create(
            name="starter",
            defaults={
                "description": "Plan inicial TEDEN Starter",
                "monthly_price": 0,
                "commission_percent": 20,
            },
        )
        seller_profile, created = SellerProfile.objects.get_or_create(user=user)
        if not seller_profile.plan:
            seller_profile.plan = starter_plan
            seller_profile.save()
        messages.info(request, "Ya sos vendedor.")
        return redirect("dashboard")

    if request.method == "POST":
        form = SellerRegistrationForm(request.POST, instance=user)
        if form.is_valid():
            try:
                vendedor = form.save(commit=False)
                vendedor.role = "seller"
                vendedor.ofrece_servicios = True
                vendedor.save()

                # 🚀 Plan Starter por defecto
                starter_plan, _ = SellerPlan.objects.get_or_create(
                    name="starter",
                    defaults={
                        "description": "Plan inicial TEDEN Starter",
                        "monthly_price": 0,
                        "commission_percent": 20,
                    },
                )

                seller_profile, created = SellerProfile.objects.get_or_create(user=vendedor)
                seller_profile.plan = starter_plan
                seller_profile.save()

                # Crear la tienda para el vendedor
                from store.models import Store
                Store.objects.get_or_create(owner=vendedor, defaults={'name': f"Tienda de {vendedor.username}"})

                messages.success(
                    request,
                    "¡Ahora sos vendedor y tenés el plan Starter automáticamente asignado!",
                )
                return redirect("dashboard")

            except IntegrityError:
                messages.error(
                    request, "Ocurrió un error guardando tus datos. Intentá de nuevo."
                )
        else:
            messages.error(request, "Revisá los campos del formulario.")
    else:
        form = SellerRegistrationForm(instance=user)

    return render(request, "users/convertirse_en_vendedor.html", {"form": form})


# ─────────────────────────────────────────────────────────────
# VERIFICAR CORREO
# ─────────────────────────────────────────────────────────────
@login_required
def verify_email(request):
    try:
        verification = EmailVerificationCode.objects.get(user=request.user)
    except EmailVerificationCode.DoesNotExist:
        messages.error(request, "No se encontró ningún código de verificación.")
        return redirect("verify_email")

    if verification.verified:
        messages.info(request, "Tu correo ya fue verificado.")
        return redirect("home")

    if request.method == "POST":
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            if verification.code == code:
                verification.verified = True
                verification.save()
                messages.success(request, "¡Correo verificado correctamente!")
                return redirect("home")
            else:
                messages.error(request, "El código ingresado no es válido.")
    else:
        form = VerificationCodeForm()

    return render(request, "users/verify_email.html", {"form": form})


# ─────────────────────────────────────────────────────────────
# DASHBOARD SEGÚN ROL
# ─────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    # Si el usuario no es vendedor o no tiene perfil de vendedor, lo
    # mandamos directamente a la vista para convertirse en vendedor.
    if request.user.role != 'seller' or not hasattr(request.user, 'sellerprofile'):
        return redirect('convertirse_en_vendedor')

    store = Store.objects.filter(owner=request.user).first()
    seller_profile = SellerProfile.objects.filter(user=request.user).first()
    public_url = None
    no_store = not store
    if store and store.slug:
        try:
            public_url = reverse("public_store", args=[store.slug])
        except NoReverseMatch:
            pass

    # Enviamos todo el contexto para vendedores
    return render(
        request,
        "dashboard/dashboard_seller.html",
        {
            "store": store,
            "public_url": public_url,
            "seller_profile": seller_profile,
            "no_store": no_store,
            "user": request.user,
        },
    )


# ─────────────────────────────────────────────────────────────
# MI CUENTA (unificada)
# ─────────────────────────────────────────────────────────────
@login_required
def mi_cuenta(request):
    user = request.user
    store = None

    # Garantizar perfil si es seller
    if user.role == "seller":
        seller_profile, _ = SellerProfile.objects.get_or_create(user=user)
        store = Store.objects.filter(owner=user).first()
    else:
        seller_profile = None

    credenciales_mp = (
        getattr(user.sellerprofile, "mercadopagocredential", None)
        if user.role == "seller"
        else None
    )

    # Formulario
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos fueron actualizados correctamente.")
            return redirect("mi_cuenta")
    else:
        form = EditProfileForm(instance=user)

    planes = SellerPlan.objects.all()

    return render(
        request,
        "users/mi_cuenta.html",
        {
            "form": form,
            "es_vendedor": user.role == "seller",
            "planes": planes,
            "seller_profile": seller_profile,
            "credenciales_mp": credenciales_mp,
            "store": store,
        },
    )


# ─────────────────────────────────────────────────────────────
# ELIMINAR CUENTA
# ─────────────────────────────────────────────────────────────
@login_required
def eliminar_cuenta(request):
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, "Tu cuenta fue eliminada correctamente.")
    return redirect("home")


# ─────────────────────────────────────────────────────────────
# TÉRMINOS Y CONDICIONES
# ─────────────────────────────────────────────────────────────
def terms_and_conditions(request):
    return render(request, "users/terms_and_conditions.html")


# ─────────────────────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect("home")


# ─────────────────────────────────────────────────────────────
# RESET DE CONTRASEÑA
# ─────────────────────────────────────────────────────────────
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            if users.exists():
                user = users.first()
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    reverse("password_reset_confirm", args=[uid, token])
                )
                send_mail(
                    "Restablecé tu contraseña en TEDEN",
                    f"Hola {user.username}, hacé clic en el siguiente enlace para restablecer tu contraseña: {reset_link}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
            return redirect("password_reset_done")
    else:
        form = PasswordResetForm()
    return render(request, "users/password_reset_form.html", {"form": form})

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("password_reset_complete")
        else:
            form = SetPasswordForm(user)
        return render(request, "users/password_reset_confirm.html", {"form": form})

    return render(request, "users/password_reset_invalid.html")


# ─────────────────────────────────────────────────────────────
# ACTIVAR SERVICIOS
# ─────────────────────────────────────────────────────────────
@login_required
def activar_servicios(request):
    if request.method == "POST":
        user = request.user
        user.ofrece_servicios = True
        user.save()
        messages.success(request, "¡Ahora podés ofrecer servicios!")
    return redirect("dashboard")


@login_required
def dejar_de_ser_vendedor(request):
    """Revoca el rol de vendedor del usuario.

    Acceso: POST desde la página de 'Mi cuenta'.
    Efectos:
    - Cambia user.role a 'buyer'
    - Elimina el SellerProfile si existe
    - Marca la tienda como inactiva si existe
    - Desactiva la opción de ofrecer servicios
    """
    user = request.user
    if request.method != 'POST':
        messages.error(request, 'Solicitud inválida.')
        return redirect('mi_cuenta')

    if user.role != 'seller':
        messages.info(request, 'No sos vendedor.')
        return redirect('mi_cuenta')

    # Eliminar perfil de vendedor
    try:
        SellerProfile.objects.filter(user=user).delete()
    except Exception:
        pass

    # Desactivar tienda si existe
    store = Store.objects.filter(owner=user).first()
    if store:
        try:
            store.is_active = False
            store.save()
        except Exception:
            pass

    # Cambiar rol y opciones
    user.role = 'buyer'
    user.ofrece_servicios = False
    user.save()

    messages.success(request, 'Ya no sos vendedor. Tu tienda fue desactivada.')
    return redirect('mi_cuenta')


# ─────────────────────────────────────────────────────────────
# PLANES
# ─────────────────────────────────────────────────────────────
def _ensure_seller_profile(user):
    if not hasattr(user, "sellerprofile"):
        starter_plan = SellerPlan.objects.get(name="starter")
        SellerProfile.objects.create(user=user, plan=starter_plan)


@login_required
def elegir_plan(request):
    user = request.user
    _ensure_seller_profile(user)
    planes = SellerPlan.objects.all()
    plus_id = None
    pro_id = None
    for plan in planes:
        if plan.name.lower() == 'plus':
            plus_id = plan.id
        if plan.name.lower() == 'pro':
            pro_id = plan.id

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        try:
            plan = SellerPlan.objects.get(id=plan_id)

            # Si el plan es gratuito, actualizar directamente.
            if plan.monthly_price <= 0:
                seller_profile = user.sellerprofile
                seller_profile.plan = plan
                seller_profile.save()
                messages.success(request, f"Has cambiado al plan '{plan.name}' correctamente.")
                return redirect("mi_cuenta")

            # Si el plan tiene costo, crear preferencia de pago.
            init_point = crear_preferencia_pago_plan(plan, user)
            
            if init_point:
                return redirect(init_point)
            else:
                messages.error(request, "No se pudo iniciar el proceso de pago. Intenta de nuevo.")
                return redirect("elegir_plan")

        except SellerPlan.DoesNotExist:
            messages.error(request, "El plan seleccionado no existe.")
            return redirect("elegir_plan")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")
            return redirect("elegir_plan")

    return render(request, "plans/planes_teden.html", {
        "planes": planes,
        "plus_id": plus_id,
        "pro_id": pro_id
    })


from payments.utils import crear_preferencia_pago_plan

@login_required
def cambiar_plan(request):
    user = request.user
    _ensure_seller_profile(user)

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        try:
            plan = SellerPlan.objects.get(id=plan_id)

            # Si el plan es gratuito, actualizar directamente.
            if plan.monthly_price <= 0:
                seller_profile = user.sellerprofile
                seller_profile.plan = plan
                seller_profile.save()
                messages.success(request, f"Has cambiado al plan '{plan.name}' correctamente.")
                return redirect("mi_cuenta")

            # Si el plan tiene costo, ir a pagar.
            # El webhook se encargará de actualizar el plan una vez aprobado el pago.
            init_point = crear_preferencia_pago_plan(plan, user)
            
            if init_point:
                return redirect(init_point)
            else:
                messages.error(request, "No se pudo iniciar el proceso de pago. Intenta de nuevo.")
                return redirect("mi_cuenta")

        except SellerPlan.DoesNotExist:
            messages.error(request, "El plan seleccionado no existe.")
            return redirect("mi_cuenta")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")
            return redirect("mi_cuenta")

    # Si no es POST, redirigir a la página de la cuenta donde se muestran los planes.
    return redirect("mi_cuenta")



# ─────────────────────────────────────────────────────────────
# MERCADOPAGO (OAuth)
# ─────────────────────────────────────────────────────────────

@login_required
def conectar_mercadopago(request):
    """
    Redirige al usuario a la pantalla de autorización de MercadoPago
    """
    # Permitir reconectar aunque ya exista credencial
    if hasattr(request.user, 'sellerprofile') and request.user.sellerprofile.mercadopagocredential:
        messages.warning(request, "Ya tenés una cuenta de MercadoPago conectada. Si continuás, se reemplazará la vinculación anterior.")
        # No redirigir, permitir continuar con el flujo OAuth

    # OAuth PKCE: generar code_verifier y code_challenge
    import secrets, hashlib, base64
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode('utf-8')
    request.session['mp_code_verifier'] = code_verifier
    redirect_uri = settings.MP_REDIRECT_URI
    client_id = settings.MP_CLIENT_ID
    auth_url = (
        "https://auth.mercadopago.com.ar/authorization"
        f"?client_id={client_id}&response_type=code&platform_id=mp&redirect_uri={redirect_uri}"
        f"&code_challenge={code_challenge}&code_challenge_method=S256"
    )
    return redirect(auth_url)


@csrf_exempt
@login_required
def mp_callback(request):
    """
    Callback de MercadoPago después de autorizar. Se intercambia el código por tokens.
    """
    import logging
    logger = logging.getLogger("mercadopago_oauth")
    # Configure logger to print to console
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.debug("--- INICIO CALLBACK MERCADOPAGO ---")
    code = request.GET.get("code")
    logger.debug(f"Paso 1: Código de autorización recibido: {code}")

    if not code:
        messages.error(request, "❌ No se pudo conectar con MercadoPago. Código no recibido.")
        logger.error("Error: No se recibió código de autorización de MercadoPago.")
        return redirect("mi_cuenta")

    code_verifier = request.session.get('mp_code_verifier')
    logger.debug(f"Paso 2: Code verifier recuperado de la sesión: {code_verifier}")

    data = {
        "grant_type": "authorization_code",
        "client_id": settings.MP_CLIENT_ID,
        "client_secret": settings.MP_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.MP_REDIRECT_URI,
        "code_verifier": code_verifier,
    }
    # Redact client_secret before logging
    log_data = data.copy()
    log_data['client_secret'] = '***REDACTED***'
    logger.debug(f"Paso 3: Enviando los siguientes datos a /oauth/token: {log_data}")

    try:
        r = requests.post("https://api.mercadopago.com/oauth/token", data=data)
        r.raise_for_status()
        logger.debug(f"Paso 4: Respuesta de /oauth/token (Status {r.status_code}):\n{r.text}")
    except requests.RequestException as e:
        error_response = e.response.text if e.response else str(e)
        logger.error(f"Error al intercambiar código por token: {error_response}")
        messages.error(request, f"❌ Error al conectar con MercadoPago: {e}")
        return redirect("mi_cuenta")

    tokens = r.json()
    access_token = tokens.get("access_token")
    logger.debug(f"Paso 5: Token de acceso extraído: {access_token}")

    # Verificación extra: validar el access_token recibido
    try:
        logger.debug("Paso 6: Validando el nuevo token de acceso con /users/me")
        r_token = requests.get("https://api.mercadopago.com/users/me", headers={"Authorization": f"Bearer {access_token}"})
        logger.debug(f"Paso 7: Respuesta de /users/me (Status {r_token.status_code}):\n{r_token.text}")
        if r_token.status_code != 200:
            messages.error(request, f"❌ El token de acceso generado por MercadoPago no es válido (Status: {r_token.status_code}). Revisa las credenciales de tu aplicación en MercadoPago.")
            return redirect("mi_cuenta")
    except Exception as ex:
        logger.error(f"Error fatal al validar el access_token: {ex}")
        messages.error(request, "❌ Ocurrió un error inesperado al validar la conexión con MercadoPago.")
        return redirect("mi_cuenta")

    # Guardar los datos en el usuario
    try:
        mp_user_id = tokens.get("user_id")
        # Buscar si otro usuario tiene este mercadopago_user_id
        from users.models import User
        otro = User.objects.filter(mercadopago_user_id=mp_user_id).exclude(id=request.user.id).first()
        if otro:
            nombre_otro = otro.username
            # Desvincular al otro usuario
            otro.mercadopago_user_id = None
            otro.mercadopago_access_token = None
            otro.mercadopago_refresh_token = None
            otro.save()
            messages.warning(request, f"La cuenta de MercadoPago estaba vinculada a {nombre_otro}. Se ha desvinculado y ahora está asociada a tu usuario.")
        logger.debug(f"Paso 8: Guardando datos para el usuario {request.user.username} (MP User ID: {mp_user_id})")
        request.user.mercadopago_user_id = mp_user_id
        request.user.mercadopago_access_token = access_token
        request.user.mercadopago_refresh_token = tokens.get("refresh_token")
        request.user.save()
        logger.debug("Paso 9: Datos guardados correctamente en el modelo User.")
    except IntegrityError:
        logger.error(f"Error de integridad al guardar datos de MP para el usuario: {request.user.username}")
        messages.error(request, "❌ Error inesperado al vincular MercadoPago.")
        return redirect("mi_cuenta")

    # Sincronizar con el modelo Store
    store, _ = Store.objects.get_or_create(
        owner=request.user,
        defaults={'name': f"Tienda de {request.user.username}"}
    )
    store.mercadopago_connected = True
    store.mercadopago_user_id = tokens.get("user_id")
    store.mercadopago_access_token = tokens.get("access_token")
    store.mercadopago_refresh_token = tokens.get("refresh_token")
    store.mercadopago_last_sync = timezone.now()
    store.save()
    logger.debug("Paso 10: Datos sincronizados con el modelo Store.")

    messages.success(request, "✅ Tu cuenta de MercadoPago fue conectada con éxito.")
    logger.debug("--- FIN CALLBACK MERCADOPAGO ---")
    return redirect("mi_cuenta")


@login_required
def desconectar_mercadopago(request):
    """
    Elimina las credenciales guardadas del vendedor y actualiza el estado en la tienda.
    """
    user = request.user
    # Limpiar datos de MercadoPago en el modelo User
    user.mercadopago_user_id = None
    user.mercadopago_access_token = None
    user.mercadopago_refresh_token = None
    user.save(update_fields=["mercadopago_user_id", "mercadopago_access_token", "mercadopago_refresh_token"])

    # Limpiar datos de MercadoPago en el modelo Store
    try:
        store = Store.objects.get(owner=user)
        store.mercadopago_connected = False
        store.mercadopago_user_id = None
        store.mercadopago_access_token = None
        store.mercadopago_refresh_token = None
        store.mercadopago_last_sync = timezone.now()
        store.save()
    except Store.DoesNotExist:
        pass

    # Limpiar credenciales del perfil de vendedor (si existe el modelo)
    if hasattr(user, 'sellerprofile'):
        perfil = user.sellerprofile
        if hasattr(perfil, 'mercadopagocredential') and perfil.mercadopagocredential:
            perfil.mercadopagocredential.delete()
            perfil.mercadopagocredential = None
            perfil.save()

    messages.success(request, "🔌 Desconectaste tu cuenta de MercadoPago.")
    return redirect("mi_cuenta")
