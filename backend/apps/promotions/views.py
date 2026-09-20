from django.shortcuts import render
from django.utils import timezone
from .models import Coupon, Banner
from apps.catalog.models import Product


def offers_view(request):
    """Special promotional discounts and on-sale audio equipment."""
    now = timezone.now()
    active_coupons = Coupon.objects.filter(is_active=True, valid_from__lte=now, valid_to__gte=now)
    sale_products = Product.objects.filter(is_active=True, is_on_sale=True).select_related('brand').prefetch_related('images')
    banners = Banner.objects.filter(is_active=True)

    context = {
        'coupons': active_coupons,
        'sale_products': sale_products,
        'banners': banners,
    }
    return render(request, 'offers.html', context)
