from decimal import Decimal
from django.shortcuts import render
from .utils import get_or_create_cart


def cart_view(request):
    """Shopping cart page view."""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related(
        'product', 'product__brand', 'product__category'
    ).prefetch_related('product__images')

    cart_subtotal = cart.subtotal
    shipping_cost = Decimal('0.00') if cart_subtotal >= Decimal('99.00') else Decimal('9.99')
    cart_total = cart_subtotal + shipping_cost

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'shipping_cost': shipping_cost,
        'cart_total': cart_total,
        'discount_amount': None,
    }
    return render(request, 'cart.html', context)
