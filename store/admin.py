# apps/store/admin.py

from django.contrib import admin
from .models import Store, StoreBlock

admin.site.register(Store)
admin.site.register(StoreBlock)
