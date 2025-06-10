from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard_admin'),
    path('usuarios/', views.manage_users, name='manage_users'),
    path('productos/', views.manage_products, name='manage_products'),
    path('estadisticas/', views.site_statistics, name='site_statistics'),
    path('productos/toggle/<int:product_id>/', views.toggle_product, name='toggle_product'),
    path('usuarios/buscar/', views.manage_users, name='search_users'),
    path('productos/buscar/', views.manage_products, name='search_products'),
    path('productos/toggle/<int:product_id>/', views.toggle_product, name='toggle_product'),
    path('productos/<int:product_id>/toggle/', views.toggle_product, name='toggle_product'),
    path('usuarios/<int:user_id>/toggle/', views.toggle_user, name='toggle_user'),
    path('panel-admin/borrar-usuarios/', views.borrar_usuarios, name='borrar_usuarios'),

]
