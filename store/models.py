# apps/store/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class StorePage(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE)

class StoreBlock(models.Model):
    store = models.ForeignKey(StorePage, on_delete=models.CASCADE)
    block_type = models.CharField(choices=[
        ('hero', 'Hero'),
        ('about', 'Sobre mí'),
        ('products', 'Productos'),
        ('testimonial', 'Testimonio'),
        ('contact', 'Contacto'),
    ], max_length=50)
    content = models.JSONField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
