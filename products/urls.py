from . import views
from django.urls import path
from .views import add_product


urlpatterns = [
    path('add/', add_product, name='add_product'),
      path('inventory/', views.inventory, name='inventory'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('mi-tienda/', views.manage_store, name='manage_store'),

]
