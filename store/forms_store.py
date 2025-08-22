from django import forms
from .models import Store

class StoreEditForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'slug', 'is_active', 'description', 'logo', 'banner', 'contact_email', 'contact_phone', 'address']
        widgets = {
            'slug': forms.TextInput(attrs={'placeholder': 'mi-tienda-unica'}),
            'name': forms.TextInput(attrs={'placeholder': 'Nombre de la tienda'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción de la tienda'}),
            'address': forms.TextInput(attrs={'placeholder': 'Dirección'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Email de contacto'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Teléfono de contacto'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if Store.objects.filter(slug=slug).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Este slug ya está en uso. Elegí otro.")
        return slug


class StoreCreateForm(forms.Form):
    name = forms.CharField(
        label='Nombre de tu tienda',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Mi Tienda'
        })
    )
