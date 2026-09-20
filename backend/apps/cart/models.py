from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.catalog.models import Product


class Cart(models.Model):
    """Shopping cart supporting both authenticated users and guest sessions."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        ordering = ['-updated_at']

    @property
    def total_items(self):
        """Total number of individual product units in the cart."""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Subtotal of all active products in the cart using effective prices."""
        return sum(item.subtotal for item in self.items.select_related('product'))

    @property
    def total(self):
        """Total cart amount before coupon discounts or shipping."""
        return self.subtotal

    def __str__(self):
        owner = self.user.email if self.user else f"Guest ({self.session_key})"
        return f"Cart of {owner} ({self.total_items} items)"


class CartItem(models.Model):
    """Individual product item inside a shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product')
        ]
        ordering = ['-created_at']

    @property
    def unit_price(self):
        return self.product.effective_price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Cart #{self.cart_id}"
