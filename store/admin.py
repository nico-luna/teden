# apps/store/admin.py

from django.contrib import admin
from .models import StorePage, StoreBlock

admin.site.register(StorePage)
admin.site.register(StoreBlock)
