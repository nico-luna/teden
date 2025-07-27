from django.shortcuts import render
from django.urls import path, include
from django.contrib.auth.views import LoginView

from orders.views import mis_compras
from . import views
from users.views import conectar_mercadopago, mp_callback, desconectar_mercadopago
urlpatterns = [
     path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
     path('logout/', views.logout_view, name='logout'),
     path('register/', views.register, name='register'),
     path('verificar-email/', views.verify_email, name='verify_email'),
     path('convertirse-en-vendedor/', views.convertirse_en_vendedor, name='convertirse_en_vendedor'),
     path('dashboard/seller/', views.dashboard, name='dashboard_seller'),
     path('elegir-plan/', views.elegir_plan, name='elegir_plan'),
     path('cambiar-plan/', views.cambiar_plan, name='cambiar_plan'),


    # Mi cuenta
     path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
     path('mi-cuenta/editar/', views.mi_cuenta, name='mi_cuenta_edit'),
     path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),

     path('terminos/', views.terms_and_conditions, name='terms_and_conditions'),

     path('accounts/', include('allauth.urls')), 

     path('products/', include('products.urls')),
    
     path('dashboard/', include('dashboard.urls')),
     path('dashboard/', views.dashboard, name='dashboard'),

     path('password-reset/', views.password_reset_request, name='password_reset'),
     path('password-reset/done/', lambda r: render(r, 'users/password_reset_done.html'), name='password_reset_done'),
     path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
     path('password-reset/complete/', lambda r: render(r, 'users/password_reset_complete.html'), name='password_reset_complete'),
     
     path('activar-servicios/', views.activar_servicios, name='activar_servicios'),

     path('mis-compras/', mis_compras, name='mis_compras'),

     path("mercadopago/oauth/", conectar_mercadopago, name="mp_conectar"),
     path("mercadopago/oauth/callback/", mp_callback, name="mp_callback"),
     path("mercadopago/desconectar/", desconectar_mercadopago, name="mp_desconectar"),
]