from django.urls import path
from .views import (
        checkout_payment, # ← ESTA LÍNEA FALTABA 
)
from .views import pay_with_mercadopago
from . import views
urlpatterns = [
    path('crear-servicio/', views.create_service, name='create_service'),
    path('disponibilidad/<int:service_id>/', views.set_availability, name='set_availability'),
    path('reservar/<int:service_id>/', views.select_appointment, name='select_appointment'),
    path('mis-turnos/', views.seller_appointments, name='seller_appointments'),
    path('cambiar-estado/<int:appointment_id>/<str:new_status>/', views.change_appointment_status, name='change_appointment_status'),
    path('disponibles/', views.ver_servicios, name='ver_servicios'),
    path('mis-turnos/', views.seller_appointments, name='seller_dashboard'),
    path('checkout/<int:appointment_id>/', checkout_payment, name='checkout_payment'),
    path('pagar-mercadopago/<int:appointment_id>/', pay_with_mercadopago, name='pay_with_mercadopago'),
]