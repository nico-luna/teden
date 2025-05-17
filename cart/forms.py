from django import forms

class CheckoutForm(forms.Form):
    full_name   = forms.CharField(max_length=100, label="Nombre completo")
    address     = forms.CharField(widget=forms.Textarea, label="Dirección de envío")
    email       = forms.EmailField(label="Correo electrónico")
    # Puedes añadir más campos (teléfono, método de pago, etc.)
