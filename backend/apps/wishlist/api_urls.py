from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.WishlistGetAPIView.as_view(), name='api_wishlist_get'),
    path('toggle/', api_views.WishlistToggleAPIView.as_view(), name='api_wishlist_toggle'),
    path('remove/', api_views.WishlistRemoveAPIView.as_view(), name='api_wishlist_remove'),
]
