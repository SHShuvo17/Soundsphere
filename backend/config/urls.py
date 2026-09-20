"""
SoundSphere URL Configuration
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # Domain URLs
    path('', include('apps.core.urls', namespace='core')),
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('', include('apps.catalog.urls', namespace='catalog')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('wishlist/', include('apps.wishlist.urls', namespace='wishlist')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('promotions/', include('apps.promotions.urls', namespace='promotions')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),

    # REST APIs
    path('api/', include([
        path('', include('apps.catalog.api_urls')),
        path('cart/', include('apps.cart.api_urls')),
        path('wishlist/', include('apps.wishlist.api_urls')),
        path('orders/', include('apps.orders.api_urls')),
        path('reviews/', include('apps.reviews.api_urls')),
        path('coupons/', include('apps.promotions.api_urls')),
    ])),

    # Unconditional direct media file serving
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),
]

# Custom error handlers
handler404 = 'apps.core.views.error_404_view'
handler403 = 'apps.core.views.error_403_view'
handler500 = 'apps.core.views.error_500_view'
