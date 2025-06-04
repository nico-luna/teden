from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model  # ✅ Usamos el modelo configurado en settings.py

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    accept_terms = forms.BooleanField(
        label='Acepto los términos y condiciones',
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'accept_terms']
