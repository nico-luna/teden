# core/urls.py
from django.urls import path
from . import views
from .views import run_collectstatic

urlpatterns = [
    path('', views.home, name='home'),
    path('run-collectstatic/', run_collectstatic),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('terminos/', views.terminos, name='terminos'),
]
