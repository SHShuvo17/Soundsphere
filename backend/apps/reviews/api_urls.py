from django.urls import path
from . import api_views

urlpatterns = [
    path('products/<int:id>/reviews/', api_views.ProductReviewsAPIView.as_view(), name='api_product_reviews'),
    path('products/<int:id>/reviews/submit/', api_views.ReviewCreateAPIView.as_view(), name='api_review_submit'),
]
