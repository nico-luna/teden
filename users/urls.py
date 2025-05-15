from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('select-role/', views.select_role, name='select_role'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('mi-cuenta/', views.mi_cuenta_vendedor, name='mi_cuenta_vendedor'),
    path('terminos/', views.terms_and_conditions, name='terms_and_conditions'),

]
