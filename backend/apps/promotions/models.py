from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order


class Coupon(models.Model):
    """Discount coupon system supporting percentage or fixed discounts with rules."""
    
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('Percentage (%)')
        FIXED = 'fixed', _('Fixed Amount ($)')

    code = models.CharField(max_length=30, unique=True, db_index=True, verbose_name=_('Coupon Code'))
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
        verbose_name=_('Discount Type')
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Discount Value'))
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Minimum Order Subtotal ($)')
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Maximum Discount Cap ($) (For % discounts)')
    )
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Total Global Usage Limit')
    )
    usage_per_user = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Max Uses Per User')
    )
    times_used = models.PositiveIntegerField(default=0, verbose_name=_('Times Used'))
    valid_from = models.DateTimeField(verbose_name=_('Valid From'))
    valid_to = models.DateTimeField(verbose_name=_('Valid Until'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active Status'))

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-valid_to']

    def calculate_discount(self, subtotal: Decimal, user=None):
        """
        Validates coupon and returns (is_valid: bool, message: str, discount_amount: Decimal).
        """
        now = timezone.now()
        if not self.is_active:
            return False, "This coupon is no longer active.", Decimal('0.00')

        if now < self.valid_from:
            return False, "This coupon promotion has not started yet.", Decimal('0.00')

        if now > self.valid_to:
            return False, "This coupon has expired.", Decimal('0.00')

        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "This coupon has reached its total usage limit.", Decimal('0.00')

        if subtotal < self.min_purchase_amount:
            return False, f"Minimum order subtotal of ${self.min_purchase_amount} required to apply this coupon.", Decimal('0.00')

        if user and user.is_authenticated:
            user_uses = CouponUsage.objects.filter(coupon=self, user=user).count()
            if user_uses >= self.usage_per_user:
                return False, f"You have already used this coupon the maximum allowed {self.usage_per_user} time(s).", Decimal('0.00')

        # Calculate discount
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = (subtotal * self.discount_value) / Decimal('100.00')
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
        else:
            discount = self.discount_value

        # Discount cannot exceed subtotal
        if discount > subtotal:
            discount = subtotal

        return True, "Coupon applied successfully!", round(discount, 2)

    def __str__(self):
        val_str = f"{self.discount_value}%" if self.discount_type == self.DiscountType.PERCENTAGE else f"${self.discount_value}"
        return f"{self.code} ({val_str} OFF)"


class CouponUsage(models.Model):
    """Tracks historical coupon redemptions per user & order."""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='coupon_usages')
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Coupon Usage')
        verbose_name_plural = _('Coupon Usages')
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code} on Order #{self.order.order_number}"


class Banner(models.Model):
    """Promotional homepage and marketing banners."""
    title = models.CharField(max_length=200, verbose_name=_('Banner Title'))
    subtitle = models.CharField(max_length=300, blank=True, verbose_name=_('Subtitle'))
    badge_text = models.CharField(max_length=50, blank=True, verbose_name=_('Badge Tag (e.g. FLASH SALE)'))
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    link_url = models.CharField(max_length=255, default='/shop/', verbose_name=_('Destination URL'))
    button_text = models.CharField(max_length=50, default='Shop Now', verbose_name=_('Button Text'))
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['display_order', '-created_at']

    @property
    def url(self):
        if self.image and bool(self.image.name):
            try:
                return self.image.url
            except ValueError:
                pass
        return ''

    def __str__(self):
        return self.title
