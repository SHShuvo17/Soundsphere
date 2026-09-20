from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.CartGetAPIView.as_view(), name='api_cart_get'),
    path('add/', api_views.CartAddAPIView.as_view(), name='api_cart_add'),
    path('update/', api_views.CartUpdateAPIView.as_view(), name='api_cart_update'),
    path('remove/', api_views.CartRemoveAPIView.as_view(), name='api_cart_remove'),
]
