"""
Global context processor for SoundSphere templates.
Provides categories, cart count, wishlist count, and global branding info.
"""

def global_context(request):
    context = {
        'SITE_NAME': 'SoundSphere',
        'SITE_TAGLINE': 'Power Your Sound — Premium Speakers & Audio Equipment',
        'cart_count': 0,
        'wishlist_count': 0,
        'nav_categories': [],
    }

    # Retrieve categories if catalog app is ready
    try:
        from apps.catalog.models import Category
        context['nav_categories'] = Category.objects.filter(is_active=True).prefetch_related('product_types')[:8]
    except Exception:
        context['nav_categories'] = []

    # Cart count
    try:
        from apps.cart.models import Cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first() if session_key else None
        
        if cart:
            context['cart_count'] = cart.total_items
    except Exception:
        context['cart_count'] = 0

    # Wishlist count
    try:
        from apps.wishlist.models import Wishlist
        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(user=request.user).first()
            if wishlist:
                context['wishlist_count'] = wishlist.items.count()
    except Exception:
        context['wishlist_count'] = 0

    return context
