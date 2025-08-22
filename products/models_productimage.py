from django.db import models

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/', blank=True, null=True)
    video = models.FileField(upload_to='products/gallery/videos/', blank=True, null=True)
    is_header = models.BooleanField(default=False, help_text='Imagen destacada/cabecera del producto')
    order = models.PositiveIntegerField(default=0, help_text='Orden en la galería')

    def __str__(self):
        return f"Imagen de {self.product.name}"
