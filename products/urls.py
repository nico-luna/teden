from . import views
from django.urls import path
from .views import add_product
from django.urls import path, include


urlpatterns = [
    path('add/', add_product, name='add_product'),
      path('inventory/', views.inventory, name='inventory'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('mi-tienda/', views.manage_store, name='manage_store'),
    path('tiendas/<str:username>/', views.public_store_view, name='public_store'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),

]
