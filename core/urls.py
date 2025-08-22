# core/urls.py
from django.urls import path
from . import views
from .views import run_collectstatic



urlpatterns = [
    path('', views.home, name='home'),
    path('run-collectstatic/', run_collectstatic),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('terminos/', views.terminos, name='terminos'),
    path('contacto/', views.contacto, name='contacto'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/<int:category_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('buscar-productos/', views.buscar_productos, name='buscar_productos'),
    path('buscar-productos-autocomplete/', views.buscar_productos_autocomplete, name='buscar_productos_autocomplete'),
]
