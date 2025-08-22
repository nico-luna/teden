from django.urls import path
from .views import (
        checkout_payment, # ← ESTA LÍNEA FALTABA 
)
from .views import pay_with_mercadopago
from . import views
urlpatterns = [
    path('crear-servicio/', views.create_service, name='create_service'),
    path('servicios/categoria/<int:categoria_id>/', views.servicios_por_categoria, name='servicios_por_categoria'),
    path('disponibilidad/<int:service_id>/', views.set_availability, name='set_availability'),
    path('reservar/<int:service_id>/', views.select_appointment, name='select_appointment'),
    path('mis-turnos/', views.seller_appointments, name='seller_appointments'),
    path('cambiar-estado/<int:appointment_id>/<str:new_status>/', views.change_appointment_status, name='change_appointment_status'),
    path('disponibles/', views.ver_servicios, name='ver_servicios'),
    path('mis-turnos/', views.seller_appointments, name='seller_dashboard'),
    path('checkout/<int:appointment_id>/', checkout_payment, name='appointments_checkout_payment'),
    path('pagar-mercadopago/<int:appointment_id>/', pay_with_mercadopago, name='pay_with_mercadopago'),
    path('buscar-servicios/', views.buscar_servicios, name='buscar_servicios'),
    path('buscar-servicios-autocomplete/', views.buscar_servicios_autocomplete, name='buscar_servicios_autocomplete'),
    path('editar-servicio/<int:service_id>/', views.edit_service, name='edit_service'),
    # path('appointment_list/', views.appointment_list, name='appointment_list'), # No existe, se debe crear
]