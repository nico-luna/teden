# views.py
from __future__ import annotations

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
                # 1️⃣ Crear usuario sin iniciarlo sesión todavía
                user = form.save(commit=False)
                user.role = "buyer"
                user.save()

                # 2️⃣ Autenticar para obtener backend
                user = authenticate(
                    request,
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                )
                if user is None:
                    messages.error(request, "Hubo un error al autenticar tu cuenta.")
                    return redirect("home")

                # 3️⃣ Generar / guardar código y marcar como NO verificado
                code = str(random.randint(100_000, 999_999))
                EmailVerificationCode.objects.update_or_create(
                    user=user, defaults={"code": code, "verified": False}
                )

                # 4️⃣ Enviar e-mail
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

                # 5️⃣ Guardar user.id en sesión y redirigir
                request.session["pending_user_id"] = user.id
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
            "core/home.html",
            {"form": form, "show_register_modal": True},
        )

    # GET
    form = CustomUserCreationForm()
    return render(request, "core/home.html", {"form": form, "show_register_modal": True})


# ─────────────────────────────────────────────────────────────
# CONVERTIRSE EN VENDEDOR
# ─────────────────────────────────────────────────────────────
@login_required
def convertirse_en_vendedor(request):
    user = request.user

    if user.role == "seller":
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
                        "price": 15000,
                        "commission_percent": 20,
                    },
                )

                SellerProfile.objects.update_or_create(
                    user=vendedor, defaults={"plan": starter_plan}
                )

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
    if request.user.role == "buyer":
        return render(request, "core/home.html")

    if request.user.role == "seller":
        store = Store.objects.filter(owner=request.user).first()
        public_url = None
        if store and store.slug:
            try:
                public_url = reverse("public_store", args=[store.slug])
            except NoReverseMatch:
                pass

        return render(
            request,
            "dashboard/dashboard_seller.html",
            {"store": store, "public_url": public_url},
        )

    return redirect("select_role")


# ─────────────────────────────────────────────────────────────
# MI CUENTA (unificada)
# ─────────────────────────────────────────────────────────────
@login_required
def mi_cuenta(request):
    user = request.user

    # Garantizar perfil + plan starter si es seller
    if user.role == "seller":
        starter_plan, _ = SellerPlan.objects.get_or_create(
            name="starter",
            defaults={
                "description": "Plan base Starter de TEDEN",
                "monthly_price": 0.00,
                "commission_percent": 20.0,
            },
        )
        seller_profile, _ = SellerProfile.objects.get_or_create(
            user=user, defaults={"plan": starter_plan}
        )
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

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        try:
            plan = SellerPlan.objects.get(id=plan_id)
            user.sellerprofile.plan = plan
            user.sellerprofile.save()
            messages.success(request, f"Elegiste el plan {plan.name}.")
            return redirect("dashboard")
        except SellerPlan.DoesNotExist:
            messages.error(request, "El plan seleccionado no existe.")

    return render(request, "users/elegir_plan.html", {"planes": planes})


@login_required
def cambiar_plan(request):
    user = request.user
    _ensure_seller_profile(user)
    planes = SellerPlan.objects.all()

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        try:
            plan = SellerPlan.objects.get(id=plan_id)
            user.sellerprofile.plan = plan
            user.sellerprofile.save()
            messages.success(request, f"Cambiaste al plan {plan.name}.")
            return redirect("dashboard")
        except SellerPlan.DoesNotExist:
            messages.error(request, "El plan seleccionado no existe.")

    return render(request, "users/elegir_plan.html", {"planes": planes})



# ─────────────────────────────────────────────────────────────
# MERCADOPAGO (OAuth)
# ─────────────────────────────────────────────────────────────

@login_required
def conectar_mercadopago(request):
    """
    Redirige al usuario a la pantalla de autorización de MercadoPago
    """
    redirect_uri = settings.MP_REDIRECT_URI
    client_id = settings.MP_CLIENT_ID
    auth_url = (
        "https://auth.mercadopago.com.ar/authorization"
        f"?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"
    )
    return redirect(auth_url)


@csrf_exempt
@login_required
def mp_callback(request):
    """
    Callback de MercadoPago después de autorizar. Se intercambia el código por tokens.
    """
    code = request.GET.get("code")
    if not code:
        messages.error(request, "❌ No se pudo conectar con MercadoPago. Código no recibido.")
        return redirect("mi_cuenta")

    data = {
        "grant_type": "authorization_code",
        "client_id": settings.MP_CLIENT_ID,
        "client_secret": settings.MP_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.MP_REDIRECT_URI,
    }

    try:
        r = requests.post("https://api.mercadopago.com/oauth/token", data=data)
        r.raise_for_status()
    except requests.RequestException as e:
        messages.error(request, f"❌ Error al conectar con MercadoPago: {e}")
        return redirect("mi_cuenta")

    tokens = r.json()
    perfil = request.user.sellerprofile

    cred, _ = MercadoPagoCredential.objects.get_or_create(seller_profile=perfil)
    cred.access_token = tokens.get("access_token")
    cred.refresh_token = tokens.get("refresh_token")
    cred.user_id = tokens.get("user_id")
    cred.live_mode = tokens.get("live_mode", False)
    cred.save()

    messages.success(request, "✅ Tu cuenta de MercadoPago fue conectada con éxito.")
    return redirect("mi_cuenta")


@login_required
def desconectar_mercadopago(request):
    """
    Elimina las credenciales guardadas del vendedor.
    """
    perfil = request.user.sellerprofile
    MercadoPagoCredential.objects.filter(seller_profile=perfil).delete()
    messages.success(request, "🔌 Desconectaste tu cuenta de MercadoPago.")
    return redirect("mi_cuenta")