from django.urls import path
from . import views
from cart.views import checkout_failure, checkout_pending

urlpatterns = [
    path('mis-planes/', views.ver_planes_disponibles, name='ver_planes'),
    path('', views.ver_planes_disponibles, name='ver_planes'),
    path('fallo/', views.checkout_failure, name='cambio_plan_fallo'),
    path('pendiente/', views.checkout_pending, name='cambio_plan_pendiente'),
    path('disponibles/', views.ver_planes_disponibles, name='ver_planes_disponibles'),
    path('confirmar-cambio/<str:plan_name>/', views.confirmar_cambio_plan, name='confirmar_cambio_plan'),
]