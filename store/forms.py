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