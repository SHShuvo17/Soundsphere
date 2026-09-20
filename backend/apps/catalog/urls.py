from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('shop/', views.shop_view, name='shop'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('product-type/<slug:slug>/', views.product_type_view, name='product_type'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('brands/', views.brands_view, name='brands'),
]
