from django import forms
from .models import BillingInfo

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingInfo
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'province', 'postal_code']
        labels = {
            'full_name': 'Nombre completo',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'city': 'Ciudad',
            'province': 'Provincia',
            'postal_code': 'Código postal',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }