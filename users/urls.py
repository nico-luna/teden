from django.shortcuts import render
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from store import views as store_views
urlpatterns = [
     path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
     path('logout/', views.logout_view, name='logout'),
     path('register/', views.register, name='register'),
     path('verificar-email/', views.verify_email, name='verify_email'),
     path('convertirse-en-vendedor/', views.convertirse_en_vendedor, name='convertirse_en_vendedor'),
     path('dashboard/seller/', views.dashboard, name='dashboard_seller'),


    # Mi cuenta comprador
     path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),

    # Mi cuenta vendedor
     path('mi-cuenta-vendedor/', views.mi_cuenta_vendedor, name='mi_cuenta_vendedor'),

     path('terminos/', views.terms_and_conditions, name='terms_and_conditions'),

     path('accounts/', include('allauth.urls')), 

     path('store/', include('store.urls')),
     path('products/', include('products.urls')),
    
     path('dashboard/', include('dashboard.urls')),
     path('dashboard/', views.dashboard, name='dashboard'),

     path('password-reset/', views.password_reset_request, name='password_reset'),
     path('password-reset/done/', lambda r: render(r, 'users/password_reset_done.html'), name='password_reset_done'),
     path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
     path('password-reset/complete/', lambda r: render(r, 'users/password_reset_complete.html'), name='password_reset_complete'),
     
     path('activar-servicios/', views.activar_servicios, name='activar_servicios'),
]