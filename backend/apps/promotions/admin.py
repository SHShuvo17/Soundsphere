from django.contrib import admin
from django.utils.html import format_html
from .models import Coupon, CouponUsage, Banner


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_display', 'min_purchase_amount', 
        'usage_counter', 'valid_from', 'valid_to', 'is_active'
    )
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    list_editable = ('is_active',)

    def discount_display(self, obj):
        if obj.discount_type == Coupon.DiscountType.PERCENTAGE:
            cap = f" (max ${obj.max_discount_amount})" if obj.max_discount_amount else ""
            return f"{obj.discount_value}% OFF{cap}"
        return f"${obj.discount_value} OFF"
    discount_display.short_description = 'Discount'

    def usage_counter(self, obj):
        limit = obj.usage_limit if obj.usage_limit else '∞'
        return f"{obj.times_used} / {limit}"
    usage_counter.short_description = 'Redemptions'


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'order', 'used_at')
    search_fields = ('coupon__code', 'user__email', 'order__order_number')
    list_filter = ('used_at',)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge_text', 'link_url', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title', 'subtitle', 'badge_text')
