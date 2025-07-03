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
from plans.models import SellerPlan

from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    EditProfileForm,
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
                user.role = 'buyer'
                user.save()
                login(request, user)

                import random
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

        # 🔁 En todos los casos con POST, volvemos al home con el modal abierto
        return render(request, 'core/home.html', {
            'form': form,
            'show_register_modal': True
        })

    # 🟢 Si es GET, mostramos el modal vacío o cerrado, pero con el form igual
    form = CustomUserCreationForm()
    return render(request, 'core/home.html', {
        'form': form,
        'show_register_modal': request.GET.get('register', False)  # Por si querés mostrarlo desde un GET
    })

# 🟢 CONVERTIRSE EN VENDEDOR (actualizado con SellerRegistrationForm)
from .forms import SellerRegistrationForm  # asegurate de importar el form
from plans.models import SellerProfile
from .models import EmailVerificationCode


@login_required
def convertirse_en_vendedor(request):
    user = request.user

    if user.role == 'seller':
        messages.info(request, "Ya sos vendedor.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, instance=user)
        if form.is_valid():
            vendedor = form.save(commit=False)
            vendedor.role = 'seller'
            vendedor.ofrece_servicios = True
            vendedor.save()

            # 🚀 Crear SellerProfile con plan Starter si no existe
            if not hasattr(vendedor, 'sellerprofile'):
                starter_plan = SellerPlan.objects.get(name='starter')
                SellerProfile.objects.get_or_create(user=vendedor, defaults={'plan': starter_plan})
            messages.success(request, "¡Ahora sos vendedor en TEDEN!")
            return redirect('elegir_plan')
    else:
        form = SellerRegistrationForm(instance=user)

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


# 🟢 MI CUENTA (UNIFICADA)
@login_required
def mi_cuenta(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos fueron actualizados correctamente.")
            return redirect('home')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'users/mi_cuenta.html', {
        'form': form,
        'es_vendedor': request.user.role == 'seller',
        'planes': SellerPlan.objects.all(),
    })



# 🟢 ELIMINAR CUENTA
@login_required
def eliminar_cuenta(request):
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, "Tu cuenta fue eliminada correctamente.")
    return redirect('home')

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


# 🟢 Activar servicios para vendedores
@login_required
def activar_servicios(request):
    if request.method == 'POST':
        user = request.user
        user.ofrece_servicios = True
        user.save()
        messages.success(request, "¡Ahora podés ofrecer servicios!")
    return redirect('seller_dashboard')

# 🟢 ELEGIR PLAN   
@login_required
def elegir_plan(request):
    user = request.user
    vendedor = user if user.role == 'seller' else None

    # ⚠️ Si ya tiene perfil con plan asignado, lo redirigimos
    if not hasattr(vendedor, 'sellerprofile'):
        starter_plan = SellerPlan.objects.get(name='starter')
        SellerProfile.objects.get_or_create(user=vendedor, defaults={'plan': starter_plan})

    planes = SellerPlan.objects.all()

    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        try:
            plan = SellerPlan.objects.get(id=plan_id)

            # Crear perfil si no existe
            if not hasattr(user, 'sellerprofile'):
                SellerProfile.objects.create(user=user, plan=plan)
            else:
                user.sellerprofile.plan = plan
                user.sellerprofile.save()

            messages.success(request, f"Elegiste el plan {plan.name}.")
            return redirect('dashboard')
        except SellerPlan.DoesNotExist:
            messages.error(request, "El plan seleccionado no existe.")

    return render(request, 'users/elegir_plan.html', {'planes': planes})

# 🟢 CAMBIAR PLAN

def ensure_seller_profile(user):
    if not hasattr(user, 'sellerprofile'):
        # Si no tiene perfil de vendedor, creamos uno con el plan Starter
        starter_plan = SellerPlan.objects.get(name='starter')
        SellerProfile.objects.create(user=user, plan=starter_plan)
@login_required
def cambiar_plan(request):
    user = request.user
    ensure_seller_profile(user)
    planes = SellerPlan.objects.all()

    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        try:
            plan = SellerPlan.objects.get(id=plan_id)
            user.sellerprofile.plan = plan
            user.sellerprofile.save()
            messages.success(request, f"Cambiaste al plan {plan.name}.")
            return redirect('dashboard')
        except SellerPlan.DoesNotExist:
            messages.error(request, "El plan seleccionado no existe.")

    return render(request, 'users/elegir_plan.html', {'planes': planes})
