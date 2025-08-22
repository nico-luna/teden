from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)  # 🆕 Campo

    def __str__(self):
        return self.name

    @classmethod
    def get_default_category(cls):
            return cls.objects.get_or_create(name="Sin categorizar")[0]
    

class Product(models.Model):
    is_active = models.BooleanField(default=True)
    is_promoted = models.BooleanField(default=False)  # Nuevo campo para productos promocionados

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sold_products'  # Evitamos conflicto
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_products'  # Evitamos conflicto
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    # El campo image principal se puede mantener para la portada
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    # Relación a galería de imágenes
    # (La clase ProductImage está en models_productimage.py)
    file = models.FileField(upload_to='products/files/', blank=True, null=True)  # 📎 Campo nuevo

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
