from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Wishlist, WishlistItem
from apps.catalog.models import Product


class WishlistGetAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'items': [], 'wishlist_count': 0})

        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        items = []
        for item in wishlist.items.select_related('product', 'product__brand'):
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'brand': item.product.brand.name,
                'price': str(item.product.effective_price),
                'image_url': item.product.primary_image.url if item.product.primary_image else '/static/images/placeholder-speaker.svg',
            })
        return Response({
            'items': items,
            'wishlist_count': wishlist.items.count()
        })


class WishlistToggleAPIView(APIView):
    """Toggles saving/removing a product from user's wishlist."""
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'redirect': True, 'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
        if item:
            item.delete()
            action = 'removed'
            message = 'Removed from wishlist.'
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            action = 'added'
            message = 'Added to wishlist.'

        return Response({
            'action': action,
            'message': message,
            'wishlist_count': wishlist.items.count()
        })


class WishlistRemoveAPIView(APIView):
    """Removes a product from wishlist."""
    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        product_id = request.data.get('product_id')
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).delete()

        return Response({
            'message': 'Item removed from wishlist.',
            'wishlist_count': wishlist.items.count()
        })
