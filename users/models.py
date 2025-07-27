from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Modelo personalizado de usuario
class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=[('buyer', 'Comprador'), ('seller', 'Vendedor')],
        blank=True,
        null=True
    )
    ofrece_servicios = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Datos para vendedores
    cuit_cuil = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# Código de verificación de email
class EmailVerificationCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - Código: {self.code}"
