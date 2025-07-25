from django.urls import path
from . import views

urlpatterns = [
    path('ordenes/', views.seller_orders, name='seller_orders'),
    path('orden/<str:order_number>/', views.order_detail, name='order_detail'),
    path('orden/<str:order_number>/estado/<str:status>/', views.update_order_status, name='update_order_status'),
    path('detalle-compra/<int:pk>/', views.detalle_compra, name='detalle_compra'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
]
