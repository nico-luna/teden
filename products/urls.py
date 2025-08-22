from . import views
from django.urls import path
from .views import add_product
from django.urls import path, include

urlpatterns = [
  path('add/', add_product, name='add_product'),
  path('inventory/', views.inventory, name='inventory'),
  path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
  path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
  path('categories/', views.category_list, name='category_list'),
  path('categories/add/', views.add_category, name='add_category'),
  path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
  path('detalle/<int:product_id>/', views.product_detail, name='product_detail'),
  path('detalle-json/<int:product_id>/', views.product_detail_ajax, name='product_detail_ajax'),
  # Galería de producto
  path('gallery/set-header/<int:media_id>/', views.set_header_image, name='set_header_image'),
  path('gallery/delete/<int:media_id>/', views.delete_gallery_media, name='delete_gallery_media'),
  path('gallery/move/<int:media_id>/<str:direction>/', views.move_gallery_media, name='move_gallery_media'),
  path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
  path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),

]
