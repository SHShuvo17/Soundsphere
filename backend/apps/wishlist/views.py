from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wishlist


@login_required
def wishlist_view(request):
    """Customer wishlist page."""
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product', 'product__brand').prefetch_related('product__images')
    return render(request, 'wishlist.html', {'wishlist': wishlist, 'wishlist_items': items})
