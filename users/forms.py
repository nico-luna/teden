from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    accept_terms = forms.BooleanField(
        label='Acepto los términos y condiciones',
        required=True,
        error_messages={
            'required': 'Debés aceptar los términos y condiciones para continuar.'
        }
    )
    

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'accept_terms']
        labels = {
            'username': 'Usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        error_messages = {
            'username': {
                'required': 'Este campo es obligatorio.',
            },
            'email': {
                'required': 'Este campo es obligatorio.',
                'invalid': 'Ingresá un correo electrónico válido.',
            },
            'password1': {
                'required': 'Este campo es obligatorio.',
            },
            'password2': {
                'required': 'Este campo es obligatorio.',
            },
        }
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email__iexact=email).exists():
        raise forms.ValidationError("Ya existe una cuenta con este correo electrónico. Iniciá sesión o recuperá tu contraseña.")
    return email


class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        label='Código de verificación',
        max_length=6,
        error_messages={
            'required': 'Por favor ingresá el código que recibiste por correo.'
        }
    )

class CustomUserChangeForm(UserChangeForm):
    password = None  # Para que no aparezca el campo de contraseña

    class Meta:
        model = User
        fields = [
            'username', 'email',
            'cuit_cuil', 'direccion', 'provincia',
            'pais', 'codigo_postal', 'telefono'
        ]
        labels = {
            'username': 'Usuario',
            'email': 'Correo electrónico',
            'cuit_cuil': 'CUIT/CUIL',
            'direccion': 'Dirección',
            'provincia': 'Provincia',
            'pais': 'País',
            'codigo_postal': 'Código Postal',
            'telefono': 'Teléfono',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
            raise forms.ValidationError("El usuario solo puede contener letras, números y guiones bajos (3 a 30 caracteres).")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.")
        return password
    
    