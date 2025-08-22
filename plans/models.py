
from django.db import models
from users.models import User

class SellerPlan(models.Model):
    PLAN_CHOICES = [
        ('starter', 'TEDEN Starter'),
        ('plus', 'TEDEN Plus'),
        ('pro', 'TEDEN Pro'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    description = models.TextField()
    monthly_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    max_products = models.PositiveIntegerField(null=True, blank=True)
    max_services = models.PositiveIntegerField(null=True, blank=True)
    max_stores = models.PositiveIntegerField(null=True, blank=True)
    promoted_products = models.PositiveIntegerField(default=0)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)

    def __str__(self):
        return dict(self.PLAN_CHOICES).get(self.name, self.name)

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SellerPlan, on_delete=models.SET_NULL, null=True, blank=True)

    # 👇 Relación con MercadoPagoCredential (usamos related_name para evitar el conflicto)
    mercadopagocredential = models.OneToOneField(
        'plans.MercadoPagoCredential',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='seller_profile_reverse'  # 🔑 clave para que no choque con reverso automático
    )

    def __str__(self):
        return f"Perfil de vendedor: {self.user.username}"

class MercadoPagoCredential(models.Model):
    # 🔄 También puedes usar related_name si querés acceder desde SellerProfile a MP Credential
    seller_profile = models.OneToOneField(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name='mercado_cred'
    )
    access_token = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    live_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"Credenciales MP para {self.seller_profile.user.username}"