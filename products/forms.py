from django import forms
from .models import Product

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
        }
        labels = {
            'name': 'Product Name',
            'description': 'Description',
            'price': 'Price',
            'stock': 'Stock',
            'image': 'Image',
        }  

        # products/forms.py
from django import forms
from .models import Store

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

# from django import forms
# from .models import Store
#
# class StoreForm(forms.ModelForm):
#     class Meta:
#         model = Store
#         fields = ['name', 'description', 'logo', 'banner']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control'}),
#             'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),    
#             'banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#         }     