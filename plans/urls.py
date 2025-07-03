from django.urls import path
from . import views

urlpatterns = [
    path('mis-planes/', views.ver_planes_disponibles, name='ver_planes'),
    path('cambiar-plan/<str:plan_name>/', views.cambiar_plan, name='cambiar_plan'),
]