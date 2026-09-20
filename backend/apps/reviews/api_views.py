from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Review
from apps.catalog.models import Product
from apps.orders.models import Order


class ProductReviewsAPIView(APIView):
    """Lists approved reviews for a given product."""
    def get(self, request, id):
        product = get_object_or_404(Product, id=id, is_active=True)
        reviews = Review.objects.filter(product=product, is_approved=True).select_related('user')
        
        data = []
        for r in reviews:
            data.append({
                'id': r.id,
                'user_name': r.user.get_full_name() or r.user.username,
                'rating': r.rating,
                'title': r.title,
                'comment': r.comment,
                'is_verified_purchase': r.is_verified_purchase,
                'created_at': r.created_at.strftime('%b %d, %Y'),
            })

        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'rating': str(product.rating),
            'review_count': product.review_count,
            'reviews': data
        })


class ReviewCreateAPIView(APIView):
    """Submits a new review for an audio product."""
    def post(self, request, id):
        if not request.user.is_authenticated:
            return Response({'error': 'Please sign in to write a review.'}, status=status.HTTP_401_UNAUTHORIZED)

        product = get_object_or_404(Product, id=id, is_active=True)

        if Review.objects.filter(user=request.user, product=product).exists():
            return Response({'error': 'You have already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = int(request.data.get('rating', 0))
        except (ValueError, TypeError):
            rating = 0
        if rating < 1 or rating > 5:
            return Response({'error': 'Rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        title = request.data.get('title', '').strip()
        comment = request.data.get('comment', '').strip()

        if not title or not comment:
            return Response({'error': 'Title and comment are required.'}, status=status.HTTP_400_BAD_REQUEST)

        is_verified = Order.objects.filter(
            user=request.user,
            order_status=Order.OrderStatus.DELIVERED,
            items__product=product
        ).exists()

        if not is_verified:
            return Response({'error': 'Reviews require a delivered purchase.'}, status=status.HTTP_403_FORBIDDEN)

        review = Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=is_verified,
            is_approved=False
        )

        return Response({
            'message': 'Review submitted successfully!',
            'review_id': review.id,
            'new_product_rating': str(product.rating),
            'new_review_count': product.review_count,
        }, status=status.HTTP_201_CREATED)
