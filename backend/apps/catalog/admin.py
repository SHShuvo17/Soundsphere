from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, ProductType, Brand, Product, ProductImage, ProductSpecification


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_url', 'alt_text', 'is_primary', 'display_order')


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 2
    fields = ('specification_name', 'specification_value', 'display_order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'category__name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'website', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'sku', 'brand', 'category', 'product_type', 
        'price_display', 'stock_badge', 'rating_display', 
        'is_featured', 'is_best_seller', 'is_active'
    )
    list_filter = (
        'category', 'product_type', 'brand', 'is_active', 
        'is_featured', 'is_best_seller', 'is_new_arrival', 'is_on_sale'
    )
    search_fields = ('name', 'sku', 'brand__name', 'category__name', 'product_type__name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline]
    list_editable = ('is_featured', 'is_best_seller', 'is_active')
    actions = ['make_active', 'make_inactive', 'mark_featured', 'mark_best_seller']

    fieldsets = (
        (_('Essential Information'), {
            'fields': ('name', 'slug', 'sku', 'brand', 'category', 'product_type')
        }),
        (_('Pricing & Stock'), {
            'fields': ('price', 'discount_price', 'stock_quantity', 'low_stock_threshold', 'warranty')
        }),
        (_('Descriptions'), {
            'fields': ('short_description', 'description')
        }),
        (_('Promotion & Display Badges'), {
            'fields': ('is_featured', 'is_best_seller', 'is_new_arrival', 'is_on_sale', 'is_active')
        }),
        (_('Metrics'), {
            'fields': ('rating', 'review_count', 'sold_count'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        if obj.discount_price and obj.discount_price > 0 and obj.discount_price < obj.price:
            return format_html(
                '<span style="color:#00c853; font-weight:bold;">${}</span> <del style="color:#888;">${}</del>',
                obj.discount_price, obj.price
            )
        return format_html('<b>${}</b>', obj.price)
    price_display.short_description = 'Price'

    def stock_badge(self, obj):
        if obj.stock_quantity <= 0:
            return format_html('<span style="color:#d50000; font-weight:bold;">Out of Stock ({})</span>', obj.stock_quantity)
        elif obj.stock_quantity <= obj.low_stock_threshold:
            return format_html('<span style="color:#ff9100; font-weight:bold;">Low Stock ({})</span>', obj.stock_quantity)
        return format_html('<span style="color:#00c853;">In Stock ({})</span>', obj.stock_quantity)
    stock_badge.short_description = 'Inventory'

    def rating_display(self, obj):
        return format_html('⭐ {} ({})', obj.rating, obj.review_count)
    rating_display.short_description = 'Rating'

    @admin.action(description=_('Mark selected products as active'))
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_('Mark selected products as inactive'))
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description=_('Feature selected products'))
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description=_('Mark selected products as Best Sellers'))
    def mark_best_seller(self, request, queryset):
        queryset.update(is_best_seller=True)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'display_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'specification_name', 'specification_value', 'display_order')
    list_filter = ('specification_name',)
    search_fields = ('product__name', 'specification_name', 'specification_value')
