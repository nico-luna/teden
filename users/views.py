from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from store.models import Store
from django.urls import reverse, NoReverseMatch

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
        return redirect('dashboard')

    if verification.verified:
        messages.info(request, "Tu correo ya fue verificado.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if verification.code == code:
                verification.verified = True
                verification.save()
                messages.success(request, "¡Correo verificado correctamente!")
                return redirect('dashboard')
            else:
                messages.error(request, "El código ingresado no es válido.")
    else:
        form = VerificationCodeForm()

    return render(request, 'users/verify_email.html', {'form': form})





# 🟢 DASHBOARD SEGÚN ROL
@login_required
def dashboard(request):
    if request.user.role == 'buyer':
        return render(request, 'dashboard/dashboard_buyer.html')

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

