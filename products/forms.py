from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'file', 'category']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

        labels = {
            'name': 'Nombre del producto',
            'description': 'Descripción',
            'price': 'Precio',
            'stock': 'Stock',
            'image': 'Imagen',
            'file': 'Archivo descargable',
            'category': 'Categoría',
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            # Tamaño máximo: 25 MB
            max_size = 25 * 1024 * 1024
            if file.size > max_size:
                raise forms.ValidationError("El archivo supera el tamaño máximo de 25 MB.")

            # Tipos de archivo permitidos
            valid_extensions = ['.pdf', '.zip', '.mp3', '.wav']
            import os
            ext = os.path.splitext(file.name)[1].lower()

            if ext not in valid_extensions:
                raise forms.ValidationError("Solo se permiten archivos PDF, ZIP o de audio (.mp3, .wav).")

        return file
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'name': 'Nombre de la categoría',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Ya existe una categoría con este nombre.")
        return name
    def save(self, commit=True):
        category = super().save(commit=False)
        category.name = category.name.strip()
        if commit:
            category.save()
            return category