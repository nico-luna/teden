# products/forms.py
from django import forms
from .models import Product, Store  # Importá todo arriba, no dentro de clases
from .models import Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Product Name',
            'description': 'Description',
            'price': 'Price',
            'stock': 'Stock',
            'image': 'Image',
        }

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description', 'logo', 'banner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Store Name',
            'description': 'Description',
            'logo': 'Logo',
            'banner': 'Banner',
        }
class ProductSearchForm(forms.Form):   
    query = forms.CharField(max_length=100, label="Search for products", required=False)
    category = forms.ChoiceField(choices=[('', 'All Categories')], required=False)
    min_price = forms.DecimalField(label="Min Price", required=False, decimal_places=2)
    max_price = forms.DecimalField(label="Max Price", required=False, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices += [(category.id, category.name) for category in Category.objects.all()]