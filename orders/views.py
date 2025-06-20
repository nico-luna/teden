from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden

from cart import models
from .models import Order, OrderHistory

@login_required
def seller_orders(request):
    print("ROL:", request.user.role)
    print("USER:", request.user.username)

    orders = Order.objects.filter(seller=request.user)
    print("ÓRDENES:", orders.count())

    return render(request, 'orders/seller_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, seller=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def update_order_status(request, order_number, status):
    order = get_object_or_404(Order, order_number=order_number, seller=request.user)
    if status in dict(Order.STATUS_CHOICES).keys():
        order.status = status
        order.save()
    return redirect('seller_orders')

@login_required
def update_order_status(request, order_number, status):
    order = get_object_or_404(Order, order_number=order_number, seller=request.user)
    
    if status in dict(Order.STATUS_CHOICES).keys():
        if order.status != status:
            OrderHistory.objects.create(
                order=order,
                changed_by=request.user,
                old_status=order.status,
                new_status=status
            )
            order.status = status
            order.save()
    
    return redirect('seller_orders')

from .utils import notificar_estado_orden  # asegurate de importar

@login_required
def update_order_status(request, order_number, status):
    order = get_object_or_404(Order, order_number=order_number, seller=request.user)

    if status in dict(Order.STATUS_CHOICES).keys():
        if order.status != status:
            OrderHistory.objects.create(
                order=order,
                changed_by=request.user,
                old_status=order.status,
                new_status=status
            )
            order.status = status
            order.save()

            # 🔔 Enviar notificación
            notificar_estado_orden(order)

    return redirect('seller_orders')

@login_required
def mis_compras(request):
    compras = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'core/mis_compras.html', {'compras': compras})

@login_required
@login_required
def detalle_compra(request, pk):
    compra = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, 'orders/detalle_compra.html', {'compra': compra})