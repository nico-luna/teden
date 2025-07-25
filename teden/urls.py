"""
URL configuration for teden project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),         # Página pública (home)
    path('', include('users.urls')),        # 👈 Las rutas de users se cargan en la raíz
    path('cart/', include('cart.urls')),
    path('products/', include('products.urls')),
    path('reviews/', include('reviews.urls')),
    path('store/', include('store.urls')),
    path('panel-admin/', include('admin_panel.urls')),
    path('', include('orders.urls')),
    path('turnos/', include('appointments.urls')),
    path('planes/', include('plans.urls')),

    
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
