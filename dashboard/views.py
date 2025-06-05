from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from store.models import Store

@login_required
def dashboard_seller(request):
    if request.user.role != 'seller':
        return redirect('dashboard_buyer')

    store = Store.objects.filter(owner=request.user).first()
    return render(request, 'dashboard/dashboard_seller.html', {
        'store': store
    })

@login_required
def dashboard_buyer(request):
    if request.user.role != 'buyer':
        return redirect('dashboard_seller')

    return render(request, 'dashboard/dashboard_buyer.html')
