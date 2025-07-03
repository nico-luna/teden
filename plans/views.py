from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SellerPlan, SellerProfile

@login_required
def ver_planes_disponibles(request):
    user = request.user

    if not hasattr(user, 'sellerprofile'):
        messages.error(request, "Debés convertirte en vendedor para acceder a los planes.")
        return redirect('convertirse_en_vendedor')

    perfil = user.sellerprofile
    planes = SellerPlan.objects.all().order_by('monthly_price')

    return render(request, 'plans/planes_disponibles.html', {
        'perfil': perfil,
        'planes': planes
    })


@login_required
def cambiar_plan(request, plan_name):
    user = request.user

    if not hasattr(user, 'sellerprofile'):
        messages.error(request, "No tenés un perfil de vendedor.")
        return redirect('ver_planes')

    nuevo_plan = get_object_or_404(SellerPlan, name=plan_name)
    perfil = user.sellerprofile

    if perfil.plan == nuevo_plan:
        messages.info(request, "Ya tenés este plan activo.")
    else:
        perfil.plan = nuevo_plan
        perfil.save()
        messages.success(request, f"¡Tu plan fue actualizado a {nuevo_plan.get_name_display()}!")

    return redirect('ver_planes')