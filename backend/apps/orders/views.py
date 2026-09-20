"""
SoundSphere Orders Views

Implements atomic, backend-validated checkout order processing.
- Never trusts frontend price/stock.
- Recalculates all amounts server-side.
- Uses database transactions for atomicity.
- Takes snapshots of product name, SKU, price, and shipping address.
"""
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, Payment, Shipping
from apps.cart.models import Cart, CartItem
from apps.accounts.models import Address
from apps.promotions.models import Coupon, CouponUsage
import logging

logger = logging.getLogger(__name__)
# convenience alias to avoid shadowing the module by a local `messages` variable
messages = django_messages


@login_required
def checkout_view(request):
    """
    Checkout page: displays cart summary, address selector, and payment method.
    On POST: atomically creates a verified order with backend price validation.
    """
    # Get or create cart for this user
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product__brand', 'product__category').prefetch_related('product__images')

    if not cart_items.exists():
        messages.warning(request, _('Your cart is empty. Add items before checking out.'))
        return redirect('cart:cart')

    # Backend subtotal calculation (never trust frontend)
    subtotal = Decimal('0.00')
    for item in cart_items:
        if item.product.stock_quantity <= 0:
            messages.error(request, _(f'"{item.product.name}" is out of stock. Please remove it from your cart.'))
            return redirect('cart:cart')
        if item.quantity > item.product.stock_quantity:
            messages.error(request, _(f'Only {item.product.stock_quantity} units of "{item.product.name}" available.'))
            return redirect('cart:cart')
        subtotal += item.product.effective_price * item.quantity

    shipping_cost = Decimal('0.00') if subtotal >= Decimal('99.00') else Decimal('9.99')

    # Coupon from session or POST
    coupon_code = request.POST.get('applied_coupon') or request.session.get('checkout_coupon', '')
    coupon_valid = False
    discount = Decimal('0.00')
    applied_coupon = None

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
            is_valid, msg, discount = coupon.calculate_discount(subtotal, request.user)
            if is_valid:
                coupon_valid = True
                applied_coupon = coupon
            else:
                discount = Decimal('0.00')
                coupon_code = ''
        except Coupon.DoesNotExist:
            discount = Decimal('0.00')
            coupon_code = ''

    order_total = subtotal + shipping_cost - discount

    saved_addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    if request.method == 'POST':
        return _process_checkout(
            request, cart, cart_items, subtotal, shipping_cost, discount, order_total, applied_coupon, saved_addresses
        )

    context = {
        'cart_items': cart_items,
        'cart_subtotal': subtotal,
        'order_total': order_total,
        'shipping_cost': shipping_cost,
        'discount_amount': discount,
        'coupon_code': coupon_code,
        'coupon_valid': coupon_valid,
        'saved_addresses': saved_addresses,
    }
    return render(request, 'orders/checkout.html', context)


def _process_checkout(request, cart, cart_items, subtotal, shipping_cost, discount, order_total, applied_coupon, saved_addresses):
    """Atomically creates an order, deducts stock, creates payment record."""
    payment_method_raw = request.POST.get('payment_method', 'cod').upper()
    payment_method = Order.PaymentMethod.COD if payment_method_raw == 'COD' else Order.PaymentMethod.ONLINE
    notes = request.POST.get('notes', '').strip()
    applied_coupon_code = request.POST.get('applied_coupon', '').strip()

    # Build shipping address
    saved_address_id = request.POST.get('saved_address_id')
    if saved_address_id:
        try:
            address = Address.objects.get(id=saved_address_id, user=request.user)
            address_snapshot = {
                'full_name': address.full_name,
                'phone': address.phone,
                'address_line': address.address_line,
                'city': address.city,
                'district': address.district,
                'postal_code': address.postal_code,
                'country': address.country,
            }
        except Address.DoesNotExist:
            messages.error(request, _('Invalid address selection.'))
            return redirect('orders:checkout')
    else:
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_line = (request.POST.get('address_line') or request.POST.get('address_line1', '')).strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', '').strip()

        if not all([full_name, phone, address_line, city, postal_code, country]):
            messages.error(request, _('Please fill in all required address fields.'))
            return redirect('orders:checkout')

        address_snapshot = {
            'full_name': full_name,
            'phone': phone,
            'address_line': address_line,
            'city': city,
            'district': (request.POST.get('district') or request.POST.get('state', '')).strip(),
            'postal_code': postal_code,
            'country': country,
        }

        # Save address if requested
        if request.POST.get('save_address'):
            Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line=address_line,
                city=city,
                district=address_snapshot['district'],
                postal_code=postal_code,
                country=country,
            )

    try:
        with transaction.atomic():
            # Re-verify stock and recalculate within the transaction
            verified_subtotal = Decimal('0.00')
            for item in cart_items:
                product = item.product.__class__.objects.select_for_update().get(id=item.product.id)
                if product.stock_quantity < item.quantity:
                    raise ValueError(f'Insufficient stock for "{product.name}". Only {product.stock_quantity} left.')
                verified_subtotal += product.effective_price * item.quantity

            verified_shipping = Decimal('0.00') if verified_subtotal >= Decimal('99.00') else Decimal('9.99')

            # Re-apply coupon
            verified_discount = Decimal('0.00')
            if applied_coupon_code:
                try:
                    coupon = Coupon.objects.get(code=applied_coupon_code.upper(), is_active=True)
                    is_valid, msg, verified_discount = coupon.calculate_discount(verified_subtotal, request.user)
                    if not is_valid:
                        verified_discount = Decimal('0.00')
                        applied_coupon_obj = None
                        applied_coupon_code = ''
                    else:
                        applied_coupon_obj = coupon
                except Coupon.DoesNotExist:
                    applied_coupon_obj = None
                    applied_coupon_code = ''
            else:
                applied_coupon_obj = None

            verified_total = verified_subtotal + verified_shipping - verified_discount

            # Create the Order
            order = Order.objects.create(
                user=request.user,
                shipping_address_snapshot=address_snapshot,
                subtotal=verified_subtotal,
                discount=verified_discount,
                shipping_cost=verified_shipping,
                tax=Decimal('0.00'),
                total_amount=verified_total,
                coupon_code_snapshot=applied_coupon_code,
                payment_method=payment_method,
                customer_notes=notes,
            )

            # Create OrderItems with snapshots and deduct stock
            for item in cart_items:
                product = item.product.__class__.objects.select_for_update().get(id=item.product.id)
                item_subtotal = product.effective_price * item.quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name_snapshot=product.name,
                    sku_snapshot=product.sku,
                    price_snapshot=product.effective_price,
                    quantity=item.quantity,
                    subtotal=item_subtotal,
                )
                product.stock_quantity -= item.quantity
                product.sold_count = (product.sold_count or 0) + item.quantity
                product.save(update_fields=['stock_quantity', 'sold_count'])

            # Create Payment record
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=verified_total,
                status=Order.PaymentStatus.PAID if payment_method == Order.PaymentMethod.ONLINE else Order.PaymentStatus.PENDING,
            )

            # Log coupon usage
            if applied_coupon_obj:
                CouponUsage.objects.create(coupon=applied_coupon_obj, user=request.user, order=order)
                applied_coupon_obj.times_used = (applied_coupon_obj.times_used or 0) + 1
                applied_coupon_obj.save(update_fields=['times_used'])

            # Clear the cart
            cart.items.all().delete()

            # Clear coupon session
            request.session.pop('checkout_coupon', None)

            logger.info(f'Order {order.order_number} created for user {request.user.email}, total ${verified_total}')

        messages.success(request, _(f'Order #{order.order_number} placed successfully! Check your email for confirmation.'))
        return redirect('orders:confirmation', order_number=order.order_number)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('cart:cart')
    except Exception as e:
        logger.error(f'Checkout failed for user {request.user.id}: {e}')
        messages.error(request, _('Something went wrong during checkout. Please try again or contact support.'))
        return redirect('orders:checkout')


@login_required
def order_confirmation_view(request, order_number):
    """Order confirmation page shown after successful checkout."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})


@login_required
def order_history_view(request):
    """Lists all orders placed by the authenticated customer."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    """Detailed order view with visual status timeline. User A cannot access User B's order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    items = order.items.select_related('product__brand').prefetch_related('product__images')

    # Status timeline steps
    timeline_steps = [
        ('pending', 'Order Placed', '&#128230;'),
        ('confirmed', 'Order Confirmed', '&#10003;'),
        ('processing', 'Processing', '&#9881;'),
        ('shipped', 'Shipped', '&#128666;'),
        ('out_for_delivery', 'Out for Delivery', '&#128205;'),
        ('delivered', 'Delivered', '&#127881;'),
    ]

    status_order = [s[0] for s in timeline_steps]
    current_idx = status_order.index(order.order_status) if order.order_status in status_order else 0

    return render(request, 'orders/detail.html', {
        'order': order,
        'items': items,
        'timeline_steps': timeline_steps,
        'current_status_idx': current_idx,
    })


@login_required
def cancel_order_view(request, order_number):
    """Cancels an order if it is still in a cancellable state."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if not order.can_cancel:
        messages.error(request, _('This order can no longer be cancelled. Please contact support.'))
        return redirect('orders:detail', order_number=order_number)

    if request.method == 'POST':
        with transaction.atomic():
            # Restore stock
            for item in order.items.select_related('product'):
                if item.product:
                    item.product.stock_quantity += item.quantity
                    item.product.sold_count = max(0, (item.product.sold_count or 0) - item.quantity)
                    item.product.save(update_fields=['stock_quantity', 'sold_count'])
            order.order_status = Order.OrderStatus.CANCELLED
            order.save(update_fields=['order_status'])
        messages.success(request, _(f'Order #{order.order_number} has been cancelled. Refund (if applicable) will be processed in 5–7 business days.'))
        return redirect('orders:history')

    return render(request, 'orders/cancel_confirm.html', {'order': order})
