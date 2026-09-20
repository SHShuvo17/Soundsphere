from rest_framework import generics, filters
from django.db.models import Q as _Q  # noqa: F401
from django.db.models import Q
from .models import Category, ProductType, Brand, Product
from .serializers import (
    CategorySerializer, ProductTypeSerializer, BrandSerializer, 
    ProductListSerializer, ProductDetailSerializer
)


class ProductListAPIView(generics.ListAPIView):
    """
    REST API endpoint to search, filter, and list audio products.
    """
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('brand', 'category', 'product_type').prefetch_related('images')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(brand__name__icontains=search) |
                Q(category__name__icontains=search) |
                Q(product_type__name__icontains=search) |
                Q(short_description__icontains=search)
            )

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        product_type = self.request.query_params.get('product_type')
        if product_type:
            queryset = queryset.filter(product_type__slug=product_type)

        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__slug=brand)

        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        in_stock = self.request.query_params.get('in_stock')
        if in_stock in ['true', '1']:
            queryset = queryset.filter(stock_quantity__gt=0)

        sort = self.request.query_params.get('sort', 'newest')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating')
        elif sort == 'popular':
            queryset = queryset.order_by('-sold_count')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    REST API endpoint for product detail.
    """
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category', 'product_type').prefetch_related('images', 'specifications')
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True).prefetch_related('product_types', 'products')
    serializer_class = CategorySerializer
    pagination_class = None


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'id'


class ProductTypeListAPIView(generics.ListAPIView):
    queryset = ProductType.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductTypeSerializer
    pagination_class = None


class BrandListAPIView(generics.ListAPIView):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    pagination_class = None
