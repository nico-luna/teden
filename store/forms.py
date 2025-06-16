# store/forms.py
from django import forms
from .models import Store

class StoreEditForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'slug']
        widgets = {
            'slug': forms.TextInput(attrs={'placeholder': 'mi-tienda-unica'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if Store.objects.filter(slug=slug).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Este slug ya está en uso. Elegí otro.")
        return slug
    
    from django import forms

class StoreCreateForm(forms.Form):
    name = forms.CharField(
        label='Nombre de tu tienda',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mi Tienda'})
    )
