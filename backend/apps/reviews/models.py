from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Product
from apps.orders.models import Order


class Review(models.Model):
    """Customer product review with rating and verified purchase badge."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Star Rating (1-5)')
    )
    title = models.CharField(max_length=150, verbose_name=_('Review Title'))
    comment = models.TextField(verbose_name=_('Review Comment'))
    is_verified_purchase = models.BooleanField(default=False, verbose_name=_('Verified Buyer'))
    is_approved = models.BooleanField(default=True, verbose_name=_('Approved'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Customer Review')
        verbose_name_plural = _('Customer Reviews')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_review')
        ]

    def save(self, *args, **kwargs):
        # Auto-detect if user has bought and received this product
        if not self.is_verified_purchase:
            has_delivered_order = Order.objects.filter(
                user=self.user,
                order_status=Order.OrderStatus.DELIVERED,
                items__product=self.product
            ).exists()
            if has_delivered_order:
                self.is_verified_purchase = True
                
        super().save(*args, **kwargs)
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_rating()

    def __str__(self):
        return f"{self.rating}★ review by {self.user.username} on {self.product.name}"
