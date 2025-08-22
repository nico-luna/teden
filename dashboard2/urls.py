from django.urls import path
from . import views


urlpatterns = [
    path('seller/', views.dashboard_seller, name='dashboard_seller'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),

]