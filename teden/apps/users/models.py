from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

SUBSCRIPTION_CHOICES = [
    ('starter', 'Starter'),
    ('pro', 'Pro'),
    ('diamond', 'Diamond'),
]

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    subscription = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='starter')
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

