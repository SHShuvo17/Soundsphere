from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .utils import get_or_create_cart
from apps.catalog.models import Product


class CartGetAPIView(APIView):
    """Returns cart contents and totals."""
    def get(self, request):
        cart = get_or_create_cart(request)
        items = []
        for item in cart.items.select_related('product', 'product__brand'):
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'brand': item.product.brand.name,
                'price': str(item.unit_price),
                'quantity': item.quantity,
                'subtotal': str(item.subtotal),
                'image_url': item.product.primary_image.url if item.product.primary_image else '/static/images/placeholder-speaker.svg',
            })
        return Response({
            'cart_id': cart.id,
            'items': items,
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
        })


class CartAddAPIView(APIView):
    """Adds a product to the cart or increments quantity."""
    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            quantity = int(request.data.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock_quantity <= 0:
            return Response({'error': 'Sorry, this audio product is currently out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            new_qty = cart_item.quantity + quantity
            if new_qty > product.stock_quantity:
                new_qty = product.stock_quantity
                cart_item.quantity = new_qty
                cart_item.save(update_fields=['quantity'])
                return Response({
                    'message': f'Quantity adjusted to maximum available stock ({product.stock_quantity}).',
                    'cart_count': cart.total_items,
                    'subtotal': str(cart.subtotal),
                }, status=status.HTTP_200_OK)
            else:
                cart_item.quantity = new_qty
                cart_item.save(update_fields=['quantity'])
        else:
            if quantity > product.stock_quantity:
                quantity = product.stock_quantity
            cart_item.quantity = quantity
            cart_item.save(update_fields=['quantity'])

        return Response({
            'message': f'{product.name} added to cart.',
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
        }, status=status.HTTP_200_OK)


class CartUpdateAPIView(APIView):
    """Updates quantity of a specific cart item."""
    def patch(self, request):
        item_id = request.data.get('item_id')
        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity <= 0:
            cart_item.delete()
            return Response({
                'message': 'Item removed from cart.',
                'item_quantity': 0,
                'item_subtotal': '0.00',
                'cart_count': cart.total_items,
                'subtotal': str(cart.subtotal),
            })

        if quantity > cart_item.product.stock_quantity:
            quantity = cart_item.product.stock_quantity
            cart_item.quantity = quantity
            cart_item.save(update_fields=['quantity'])
            return Response({
                'message': f'Maximum available stock reached ({quantity}).',
                'item_quantity': cart_item.quantity,
                'item_subtotal': str(cart_item.subtotal),
                'cart_count': cart.total_items,
                'subtotal': str(cart.subtotal),
            })

        cart_item.quantity = quantity
        cart_item.save(update_fields=['quantity'])

        return Response({
            'message': 'Cart updated.',
            'item_quantity': cart_item.quantity,
            'item_subtotal': str(cart_item.subtotal),
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
        })


class CartRemoveAPIView(APIView):
    """Removes an item completely from the cart."""
    def delete(self, request):
        item_id = request.data.get('item_id')
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()

        return Response({
            'message': 'Item removed.',
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
        })
