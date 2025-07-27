from django.urls import path
from . import views
app_name = "store"

urlpatterns = [
    path('tienda/ordenar-bloques/', views.update_block_order, name='update_block_order'),  # ← PRIMERO
    path('crear/', views.crear_tienda, name='crear_tienda'),
    path('mi-tienda/', views.edit_store, name='edit_store'),
    path('mi-tienda/agregar/', views.add_block, name='add_block'),
    path('mi-tienda/bloque/<int:block_id>/editar/', views.edit_block, name='edit_block'),
    path('mi-tienda/bloque/<int:block_id>/eliminar/', views.delete_block, name='delete_block'),
    # path('tienda/<slug:slug>/hero/', views.store_hero, name='store_hero'),
    path('tienda/<slug:slug>/', views.public_store, name='public_store'),  # ← DEJÁ ESTA AL FINAL SIEMPRE
]

from django.http import HttpResponse

urlpatterns += [
    path('debug-test/', lambda r: HttpResponse("Funciona la ruta!")),
]