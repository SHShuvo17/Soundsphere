from django.urls import path
from . import api_views

urlpatterns = [
    path('validate/', api_views.CouponValidateAPIView.as_view(), name='api_coupon_validate'),
]
