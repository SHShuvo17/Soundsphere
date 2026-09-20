from django.contrib import admin
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    raw_id_fields = ('product',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'items_count', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    inlines = [WishlistItemInline]

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items in Wishlist'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('wishlist', 'product', 'created_at')
    raw_id_fields = ('wishlist', 'product')
