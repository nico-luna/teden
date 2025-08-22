from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):

    gallery = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,video/*'}),
        required=False,
        label='Galería de archivos',
        help_text='Podés subir hasta 5 imágenes o videos en total.'
    )

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
            'image': 'Imagen principal',
            'file': 'Archivo descargable',
            'category': 'Categoría',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ordenar las categorías dejando "Sin categorizar" al final
        categorias = list(Category.objects.all())
        categorias_ordenadas = sorted(categorias, key=lambda c: c.name.lower() == "sin categorizar")
        self.fields['category'].queryset = Category.objects.filter(id__in=[c.id for c in categorias_ordenadas])

        # Si es un formulario nuevo, setear "Sin categorizar" como valor inicial
        if not self.instance.pk:
            try:
                sin_cat = Category.objects.get(name__iexact="Sin categorizar")
                self.fields['category'].initial = sin_cat.id
            except Category.DoesNotExist:
                pass  # Si no existe, no pasa nada

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock <= 0:
            raise forms.ValidationError('El stock debe ser mayor a 0 para publicar el producto.')
        return stock

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['file']

        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'file': 'Archivo (PDF, ZIP, MP3, WAV)',
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
        fields = ['name', 'image']  # 👉 agregamos el campo image

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # 🆕
        }

        labels = {
            'name': 'Nombre de la categoría',
            'image': 'Imagen representativa',  # 🆕
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Ya existe una categoría con este nombre.")
        return name.strip()

    def save(self, commit=True):
        category = super().save(commit=False)
        category.name = category.name.strip()
        if commit:
            category.save()
        return category