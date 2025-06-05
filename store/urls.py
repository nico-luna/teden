from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_tienda, name='crear_tienda'),
    path('mi-tienda/', views.edit_store, name='edit_store'),
    path('mi-tienda/agregar/', views.add_block, name='add_block'),
    path('mi-tienda/bloque/<int:block_id>/editar/', views.edit_block, name='edit_block'),
    path('mi-tienda/bloque/<int:block_id>/eliminar/', views.delete_block, name='delete_block'),
    path('tienda/<slug:slug>/', views.public_store, name='public_store'),
]
