from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    raw_id_fields = ('product',)
    fields = ('product', 'quantity', 'unit_price', 'subtotal', 'created_at')
    readonly_fields = ('unit_price', 'subtotal', 'created_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner_display', 'total_items', 'subtotal_display', 'created_at', 'updated_at')
    search_fields = ('user__email', 'session_key')
    list_filter = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def owner_display(self, obj):
        return obj.user.email if obj.user else f"Guest ({obj.session_key})"
    owner_display.short_description = 'Cart Owner'

    def subtotal_display(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal_display.short_description = 'Cart Subtotal'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal', 'created_at')
    raw_id_fields = ('cart', 'product')
