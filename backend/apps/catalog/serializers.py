from rest_framework import serializers
from .models import Category, ProductType, Brand, Product, ProductImage, ProductSpecification


class CategorySerializer(serializers.ModelSerializer):
    product_types_count = serializers.IntegerField(source='product_types.count', read_only=True)
    products_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'icon_svg', 'product_types_count', 'products_count')


class ProductTypeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ProductType
        fields = ('id', 'category', 'category_name', 'name', 'slug', 'description')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'website', 'description')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'url', 'alt_text', 'is_primary', 'display_order')


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ('id', 'specification_name', 'specification_value', 'display_order')


class ProductListSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    product_type_name = serializers.CharField(source='product_type.name', read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    primary_image = ProductImageSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'brand_name', 'category_name', 
            'product_type_name', 'price', 'discount_price', 'effective_price',
            'discount_percentage', 'stock_quantity', 'stock_status', 'rating',
            'review_count', 'is_featured', 'is_best_seller', 'is_new_arrival', 
            'is_on_sale', 'primary_image'
        )


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            'short_description', 'description', 'warranty', 'images', 'specifications'
        )
