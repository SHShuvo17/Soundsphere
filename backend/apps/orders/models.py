import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Product


class Order(models.Model):
    """Customer order containing pricing snapshots and fulfillment status."""
    
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('Order Placed (Pending)')
        CONFIRMED = 'confirmed', _('Order Confirmed')
        PROCESSING = 'processing', _('Processing & Audio QA')
        SHIPPED = 'shipped', _('Shipped')
        OUT_FOR_DELIVERY = 'out_for_delivery', _('Out for Delivery')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')
        RETURNED = 'returned', _('Returned')

    class PaymentMethod(models.TextChoices):
        COD = 'COD', _('Cash on Delivery')
        ONLINE = 'ONLINE', _('Online Payment Gateway')

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Payment Pending')
        PAID = 'paid', _('Paid')
        FAILED = 'failed', _('Payment Failed')
        REFUNDED = 'refunded', _('Refunded')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    order_number = models.CharField(max_length=36, unique=True, db_index=True)
    
    # Address Snapshot (immutable historical record)
    shipping_address_snapshot = models.JSONField(
        help_text=_('JSON snapshot of recipient name, phone, address, city, and country at time of checkout')
    )
    
    # Financial snapshots
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Subtotal ($)'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Discount ($)'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Shipping Cost ($)'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Tax ($)'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount ($)'))
    coupon_code_snapshot = models.CharField(max_length=50, blank=True, verbose_name=_('Applied Coupon'))
    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
        verbose_name=_('Payment Method')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name=_('Payment Status')
    )
    order_status = models.CharField(
        max_length=25,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
        verbose_name=_('Order Status')
    )
    
    customer_notes = models.TextField(blank=True, verbose_name=_('Order Notes'))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def can_cancel(self):
        return self.order_status in [self.OrderStatus.PENDING, self.OrderStatus.CONFIRMED]

    @property
    def is_delivered(self):
        return self.order_status == self.OrderStatus.DELIVERED

    def __str__(self):
        return f"Order #{self.order_number} — ${self.total_amount} ({self.get_order_status_display()})"


class OrderItem(models.Model):
    """Historical snapshot of product and price at time of order creation."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    
    # Snapshots
    product_name_snapshot = models.CharField(max_length=255)
    sku_snapshot = models.CharField(max_length=60)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.quantity}x {self.product_name_snapshot} (${self.subtotal})"


class Payment(models.Model):
    """Payment transaction details."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=30)
    transaction_id = models.CharField(max_length=120, blank=True, verbose_name=_('Transaction ID'))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Order.PaymentStatus.choices,
        default=Order.PaymentStatus.PENDING
    )
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def __str__(self):
        return f"Payment for Order #{self.order.order_number} (${self.amount} - {self.status})"


class Shipping(models.Model):
    """Fulfillment and tracking information."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_detail')
    carrier = models.CharField(max_length=100, default='SoundSphere Audio Logistics Express')
    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Shipping Detail')
        verbose_name_plural = _('Shipping Details')

    def __str__(self):
        return f"Shipping for #{self.order.order_number} ({self.carrier})"
