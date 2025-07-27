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
    

class EditProfileForm(forms.ModelForm):
    widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    profile_picture = forms.ImageField(
        required=False,
        label='Foto de perfil',
        help_text='Subí una imagen para tu perfil (opcional).'
    )
    class Meta:
        model = User
        fields = [
            'profile_picture', 'username', 'bio', 'email',
            'cuit_cuil', 'direccion', 'provincia', 'pais',
            'codigo_postal', 'telefono'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'cuit_cuil': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control','id': 'id_telefono','placeholder': 'Ej: 11 2345 6789'
}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if user.role != 'seller':
            # Ocultar campos de vendedor si es buyer
            for field in ['cuit_cuil', 'direccion', 'provincia', 'pais', 'codigo_postal', 'telefono']:
                self.fields[field].widget = forms.HiddenInput()


import re
from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

class SellerRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'cuit_cuil', 'direccion', 'provincia', 'pais',
            'codigo_postal', 'telefono'
        ]
        labels = {
            'cuit_cuil': 'CUIT/CUIL',
            'direccion': 'Dirección',
            'provincia': 'Provincia',
            'pais': 'País',
            'codigo_postal': 'Código Postal',
            'telefono': 'Teléfono',
        }
        widgets = {
            'cuit_cuil': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cuit_cuil(self):
        cuit = self.cleaned_data.get('cuit_cuil')
        if not re.match(r'^\d{11}$', cuit):
            raise forms.ValidationError("El CUIT/CUIL debe tener exactamente 11 dígitos.")
        return cuit

    def clean_codigo_postal(self):
        cp = self.cleaned_data.get('codigo_postal')
        if not re.match(r'^\d{4,5}$', cp):
            raise forms.ValidationError("El código postal debe tener entre 4 y 5 dígitos.")
        return cp

    def clean_telefono(self):
        tel = self.cleaned_data.get('telefono')
        if not re.match(r'^\+?\d{10,15}$', tel):
            raise forms.ValidationError("Ingresá un número de teléfono válido con prefijo internacional.")
        return tel

    def clean(self):
        cleaned_data = super().clean()
        campos = ['cuit_cuil', 'direccion', 'provincia', 'pais', 'codigo_postal', 'telefono']
        for campo in campos:
            if not cleaned_data.get(campo):
                self.add_error(campo, "Este campo es obligatorio.")
        return cleaned_data