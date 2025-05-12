from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProductForm

@login_required
def add_product(request):
    if request.user.role != 'seller':
        return redirect('dashboard')  # seguridad

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})
