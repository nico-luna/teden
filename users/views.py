from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from store.models import Store
from django.urls import reverse, NoReverseMatch

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    VerificationCodeForm,
)
from .models import EmailVerificationCode


# 🟢 REGISTRO
@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.role = 'buyer'  # 👈 Asignar rol comprador por defecto
                user.save()
                login(request, user)

                # Enviar código de verificación
                import random
                from django.core.mail import send_mail

                code = str(random.randint(100000, 999999))
                EmailVerificationCode.objects.create(user=user, code=code)

                send_mail(
                    subject='Verificá tu cuenta en TEDEN',
                    message=f'Tu código de verificación es: {code}',
                    from_email='no-reply@teden.com',
                    recipient_list=[user.email],
                )

                return redirect('verify_email')

            except IntegrityError:
                messages.error(request, "Este nombre de usuario o email ya está registrado.")
        else:
            messages.error(request, "Revisá los campos del formulario.")

        return render(request, 'core/home.html', {
            'form': form,
            'show_register_modal': True
        })

    # GET
    form = CustomUserCreationForm()
    return render(request, 'core/home.html', {
        'form': form,
        'show_register_modal': False
    })


# 🟢 CONVERTIRSE EN VENDEDOR
@login_required
def convertirse_en_vendedor(request):
    if request.user.role != 'buyer':
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'seller'
            user.save()
            messages.success(request, "¡Ahora sos vendedor en TEDEN!")
            return redirect('dashboard')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/convertirse_en_vendedor.html', {'form': form})

# 🟢 VERIFICAR CORREO
@login_required
def verify_email(request):
    try:
        verification = EmailVerificationCode.objects.get(user=request.user)
    except EmailVerificationCode.DoesNotExist:
        messages.error(request, "No se encontró ningún código de verificación.")
        return redirect('verify_email')

    if verification.verified:
        messages.info(request, "Tu correo ya fue verificado.")
        return redirect('home')

    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if verification.code == code:
                verification.verified = True
                verification.save()
                messages.success(request, "¡Correo verificado correctamente!")
                return redirect('home')
            else:
                messages.error(request, "El código ingresado no es válido.")
    else:
        form = VerificationCodeForm()

    return render(request, 'users/verify_email.html', {'form': form})


# 🟢 DASHBOARD SEGÚN ROL
@login_required
def dashboard(request):
    if request.user.role == 'buyer':
        return render(request, 'core/home.html')

    elif request.user.role == 'seller':
        store = Store.objects.filter(owner=request.user).first()

        public_url = None
        if store and store.slug:
            try:
                public_url = reverse('public_store', args=[store.slug])
            except NoReverseMatch:
                public_url = None

        return render(request, 'dashboard/dashboard_seller.html', {
            'store': store,
            'public_url': public_url
        })

    return redirect('select_role')


# 🟢 MI CUENTA (COMÚN)
@login_required
def mi_cuenta(request):
    return render(request, 'users/mi_cuenta.html')


# 🟢 MI CUENTA VENDEDOR (EDICIÓN)
@login_required
def mi_cuenta_vendedor(request):
    if request.user.role != 'seller':
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos fueron actualizados correctamente.")
            return redirect('mi_cuenta_vendedor')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/mi_cuenta_vendedor.html', {'form': form})


# 🟢 TÉRMINOS Y CONDICIONES
def terms_and_conditions(request):
    return render(request, 'users/terms_and_conditions.html')


# 🟢 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('home')


User = get_user_model()

# 🟢 Solicitud de reseteo de contraseña
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

# 🟢 Confirmar nueva contraseña
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
    else:
        return render(request, "users/password_reset_invalid.html")
