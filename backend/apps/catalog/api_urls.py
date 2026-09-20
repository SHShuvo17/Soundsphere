from django.urls import path
from . import api_views

urlpatterns = [
    path('products/', api_views.ProductListAPIView.as_view(), name='api_product_list'),
    path('products/<int:id>/', api_views.ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('categories/', api_views.CategoryListAPIView.as_view(), name='api_category_list'),
    path('categories/<int:id>/', api_views.CategoryDetailAPIView.as_view(), name='api_category_detail'),
    path('product-types/', api_views.ProductTypeListAPIView.as_view(), name='api_product_type_list'),
    path('brands/', api_views.BrandListAPIView.as_view(), name='api_brand_list'),
]
