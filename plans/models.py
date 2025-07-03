from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

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
    plan = models.ForeignKey(SellerPlan, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"