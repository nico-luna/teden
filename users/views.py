from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('select_role')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def select_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['buyer', 'seller']:
            request.user.role = role
            request.user.save()
            return redirect('dashboard')  # redirigimos a la vista `dashboard`
    return render(request, 'users/select_role.html')

@login_required
def dashboard(request):
    if request.user.role == 'buyer':
        return render(request, 'users/dashboard_buyer.html')
    elif request.user.role == 'seller':
        return render(request, 'users/dashboard_seller.html')
    else:
        return redirect('select_role')

from django.contrib.auth.decorators import login_required

@login_required
def mi_cuenta(request):
    return render(request, 'users/mi_cuenta.html')

from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm

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


from django.shortcuts import render

def terms_and_conditions(request):
    return render(request, 'users/terms_and_conditions.html')
