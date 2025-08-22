# plans/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import SellerPlan
from payments.utils import crear_preferencia_pago_plan

@login_required
def ver_planes_disponibles(request):
    user = request.user

    if not hasattr(user, 'sellerprofile'):
        messages.error(request, "Debés convertirte en vendedor para acceder a los planes.")
        return redirect('convertirse_en_vendedor')

    perfil = user.sellerprofile
    planes = SellerPlan.objects.all().order_by('monthly_price')

    return render(request, 'plans/planes_teden.html', {
        'perfil': perfil,
        'planes': planes
    })


@login_required
def confirmar_cambio_plan(request, plan_name):
    user = request.user

    # 1) Verifico que tenga perfil y credencial de MP
    if not hasattr(user, 'sellerprofile') or not user.sellerprofile.mercadopagocredential:
        messages.error(request, "Debés conectar tu cuenta de MercadoPago antes de cambiar de plan. Sin credencial no se puede generar el link de pago.")
        return render(request, 'plans/error_pago.html', {'error': 'Falta credencial de MercadoPago'})

    # 2) Busco el plan o muestro 404
    plan = get_object_or_404(SellerPlan, name=plan_name)

    # 3) Evito re-seleccionar el mismo plan
    if plan == user.sellerprofile.plan:
        messages.info(request, "Ya tenés este plan activo.")
        return redirect('plans:ver_planes_disponibles')

    # 4) Genero la preferencia de pago y redirijo
    try:
        preference_url = crear_preferencia_pago_plan(plan, user)
        if preference_url:
            return render(request, 'plans/ir_a_pago.html', {'preference_url': preference_url, 'plan': plan})
        else:
            error_msg = "No se pudo obtener el link de pago de MercadoPago. Por favor, contacta soporte."
            return render(request, 'plans/error_pago.html', {'preference_url': None, 'error': error_msg})
    except Exception as e:
        error_msg = f"Error al generar el link de pago: {e}"
        return render(request, 'plans/error_pago.html', {'preference_url': None, 'error': error_msg})


def checkout_success(request):
    return render(request, 'plans/exito.html')


def checkout_failure(request):
    return render(request, 'plans/fallo.html')


def checkout_pending(request):
    return render(request, 'plans/pendiente.html')


def calcular_comision_por_venta(seller_profile, monto_total):
    try:
        porcentaje = seller_profile.plan.commission_percent
        if porcentaje is None:
            raise ValueError("Porcentaje de comisión no definido.")
    except Exception:
        porcentaje = 20.0  # fallback al 20%
    return round(monto_total * (porcentaje / 100), 2)
    
# Vistas callback de MercadoPago
def checkout_success(request):
    return HttpResponse("✅ ¡Pago realizado con éxito! Tu plan se ha actualizado correctamente.")

def checkout_failure(request):
    return HttpResponse("❌ Hubo un error con el pago. No se actualizó el plan.")

def checkout_pending(request):
    return HttpResponse("⏳ El pago está pendiente. Cuando se confirme, actualizaremos tu plan.")
