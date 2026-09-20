from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, Payment, Shipping


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)
    fields = ('product', 'product_name_snapshot', 'sku_snapshot', 'price_snapshot', 'quantity', 'subtotal')
    readonly_fields = ('product_name_snapshot', 'sku_snapshot', 'price_snapshot', 'quantity', 'subtotal')


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False
    fields = ('payment_method', 'transaction_id', 'amount', 'status')


class ShippingInline(admin.StackedInline):
    model = Shipping
    extra = 0
    fields = ('carrier', 'tracking_number', 'estimated_delivery', 'shipped_at', 'delivered_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user_email', 'total_amount_display', 
        'payment_status_badge', 'order_status_badge', 'payment_method', 'created_at'
    )
    list_filter = ('order_status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__username', 'customer_notes')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'address_preview')
    inlines = [OrderItemInline, PaymentInline, ShippingInline]
    actions = ['mark_confirmed', 'mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    fieldsets = (
        (_('Order Overview'), {
            'fields': ('order_number', 'user', 'order_status', 'customer_notes', 'created_at', 'updated_at')
        }),
        (_('Financial Summary'), {
            'fields': ('subtotal', 'discount', 'shipping_cost', 'tax', 'total_amount', 'coupon_code_snapshot', 'payment_method', 'payment_status')
        }),
        (_('Shipping Destination Snapshot'), {
            'fields': ('address_preview', 'shipping_address_snapshot')
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Customer'

    def total_amount_display(self, obj):
        return format_html('<b>${:.2f}</b>', obj.total_amount)
    total_amount_display.short_description = 'Grand Total'

    def payment_status_badge(self, obj):
        colors = {'paid': '#00c853', 'pending': '#ff9100', 'failed': '#d50000', 'refunded': '#2979ff'}
        color = colors.get(obj.payment_status, '#888')
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.get_payment_status_display())
    payment_status_badge.short_description = 'Payment'

    def order_status_badge(self, obj):
        colors = {
            'pending': '#ff9100',
            'confirmed': '#2979ff',
            'processing': '#9c27b0',
            'shipped': '#00b0ff',
            'out_for_delivery': '#ff6d00',
            'delivered': '#00c853',
            'cancelled': '#d50000',
            'returned': '#757575'
        }
        color = colors.get(obj.order_status, '#888')
        return format_html('<span style="background-color:{}; color:#fff; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold;">{}</span>', color, obj.get_order_status_display())
    order_status_badge.short_description = 'Status'

    def address_preview(self, obj):
        addr = obj.shipping_address_snapshot
        if isinstance(addr, dict):
            return format_html(
                "<strong>Recipient:</strong> {}<br>"
                "<strong>Phone:</strong> {}<br>"
                "<strong>Address:</strong> {}, {}, {} {}, {}",
                addr.get('full_name', ''),
                addr.get('phone', ''),
                addr.get('address_line', ''),
                addr.get('city', ''),
                addr.get('district', ''),
                addr.get('postal_code', ''),
                addr.get('country', '')
            )
        return str(addr)
    address_preview.short_description = 'Formatted Address'

    @admin.action(description=_('Mark as Confirmed'))
    def mark_confirmed(self, request, queryset):
        queryset.update(order_status=Order.OrderStatus.CONFIRMED)

    @admin.action(description=_('Mark as Processing / Audio QA'))
    def mark_processing(self, request, queryset):
        queryset.update(order_status=Order.OrderStatus.PROCESSING)

    @admin.action(description=_('Mark as Shipped'))
    def mark_shipped(self, request, queryset):
        queryset.update(order_status=Order.OrderStatus.SHIPPED)

    @admin.action(description=_('Mark as Delivered'))
    def mark_delivered(self, request, queryset):
        queryset.update(order_status=Order.OrderStatus.DELIVERED, payment_status=Order.PaymentStatus.PAID)

    @admin.action(description=_('Mark as Cancelled'))
    def mark_cancelled(self, request, queryset):
        queryset.update(order_status=Order.OrderStatus.CANCELLED)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name_snapshot', 'sku_snapshot', 'price_snapshot', 'quantity', 'subtotal')
    search_fields = ('order__order_number', 'product_name_snapshot', 'sku_snapshot')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'transaction_id', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('order', 'carrier', 'tracking_number', 'estimated_delivery', 'shipped_at', 'delivered_at')
    search_fields = ('order__order_number', 'tracking_number', 'carrier')
