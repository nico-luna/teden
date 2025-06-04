from django.urls import path
from . import views

urlpatterns = [
    path('mi-tienda/', views.edit_store, name='edit_store'),
    path('mi-tienda/agregar/', views.add_block, name='add_store_block'),
    path('mi-tienda/bloque/<int:block_id>/editar/', views.edit_block, name='edit_store_block'),
    path('mi-tienda/bloque/<int:block_id>/eliminar/', views.delete_block, name='delete_store_block'),
    path('tienda/<int:user_id>/', views.public_store, name='public_store'),
]