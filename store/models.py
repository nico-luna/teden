from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Store(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store_profile')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    custom_css = models.TextField(blank=True, null=True)    
    custom_js = models.TextField(blank=True, null=True) 
    custom_meta = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='store_banners/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    social_links = models.JSONField(default=dict, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.name 
    def get_absolute_url(self):
        return f"/store/{self.id}/"
    def get_owner_profile_url(self):
        return f"/users/{self.owner.username}/"
    def get_products_url(self):
        return f"/store/{self.id}/products/"
    def get_reviews_url(self):
        return f"/store/{self.id}/reviews/"
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/tienda/{self.slug}/"

class StoreBlock(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="blocks")
    block_type = models.CharField(choices=[
        ('hero', 'Hero'),
        ('about', 'Sobre mí'),
        ('products', 'Productos'),
        ('testimonial', 'Testimonio'),
        ('contact', 'Contacto'),
    ], max_length=50)
    content = models.JSONField(default=dict)
    order = models.PositiveIntegerField(default=0)
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']


from django.utils.text import slugify
from .models import Store
from django.db.models import Count

def generar_slug_unico(nombre_base):
    slug_base = slugify(nombre_base)
    slug = slug_base
    contador = 1
    while Store.objects.filter(slug=slug).exists():
        slug = f"{slug_base}-{contador}"
        contador += 1
    return slug


from django.contrib.auth import get_user_model
User = get_user_model()



