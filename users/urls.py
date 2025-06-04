from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from store import views as store_views
urlpatterns = [
    path('login/',
         LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('register/', views.register, name='register'),

    path('verificar-email/', views.verify_email, name='verify_email'),

    path('select-role/', views.select_role, name='select_role'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Mi cuenta comprador
    path('mi-cuenta/',
         views.mi_cuenta,
         name='mi_cuenta'),

    # Mi cuenta vendedor
    path('mi-cuenta-vendedor/',
         views.mi_cuenta_vendedor,
         name='mi_cuenta_vendedor'),

    path('terminos/', views.terms_and_conditions, name='terms_and_conditions'),

    path('accounts/', include('allauth.urls')), 

    path('store/', include('store.urls')),


]