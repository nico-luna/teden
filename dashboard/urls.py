from django.urls import path
from . import views

urlpatterns = [
    path('seller/', views.dashboard_seller, name='dashboard_seller'),
    path('buyer/', views.dashboard_buyer, name='dashboard_buyer'),
]