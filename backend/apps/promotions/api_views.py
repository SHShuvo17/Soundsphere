from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon
from apps.cart.utils import get_or_create_cart


class CouponValidateAPIView(APIView):
    """Validates coupon code against backend cart subtotal and user redemption rules."""
    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        if not code:
            return Response({'is_valid': False, 'error': 'Coupon code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        coupon = Coupon.objects.filter(code__iexact=code).first()
        if not coupon:
            return Response({'is_valid': False, 'error': 'Invalid coupon code. Please check spelling.'}, status=status.HTTP_404_NOT_FOUND)

        # Recalculate subtotal directly on backend from cart
        cart = get_or_create_cart(request)
        subtotal = cart.subtotal

        if subtotal <= 0:
            return Response({'is_valid': False, 'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, msg, discount = coupon.calculate_discount(subtotal, user=request.user if request.user.is_authenticated else None)

        if not is_valid:
            return Response({'is_valid': False, 'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        new_total = subtotal - discount
        if new_total < Decimal('0.00'):
            new_total = Decimal('0.00')

        return Response({
            'is_valid': True,
            'code': coupon.code,
            'message': msg,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(discount),
            'new_total': str(new_total),
        }, status=status.HTTP_200_OK)
