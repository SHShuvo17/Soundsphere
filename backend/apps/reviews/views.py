from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Review
from apps.catalog.models import Product
from apps.orders.models import Order


@login_required
def submit_review_view(request, product_id):
    """Submits a customer rating and review for an audio product."""
    if request.method != 'POST':
        return redirect('catalog:shop')

    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Check if user already reviewed this product
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, _('You have already submitted a review for this product.'))
        return redirect('catalog:product_detail', slug=product.slug)

    try:
        rating = int(request.POST.get('rating', 0))
    except (ValueError, TypeError):
        rating = 0
    if rating < 1 or rating > 5:
        messages.error(request, _('Rating must be between 1 and 5.'))
        return redirect('catalog:product_detail', slug=product.slug)

    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()

    if not title or not comment:
        messages.error(request, _('Please provide both a title and comments for your review.'))
        return redirect('catalog:product_detail', slug=product.slug)

    # Check if user is a verified buyer who received this product
    is_verified = Order.objects.filter(
        user=request.user,
        order_status=Order.OrderStatus.DELIVERED,
        items__product=product
    ).exists()

    if not is_verified:
        messages.error(request, _('Reviews can be submitted after a delivered purchase.'))
        return redirect('catalog:product_detail', slug=product.slug)

    Review.objects.create(
        user=request.user,
        product=product,
        rating=rating,
        title=title,
        comment=comment,
        is_verified_purchase=is_verified,
        is_approved=False
    )

    messages.success(request, _('Thank you! Your audio review has been posted successfully.'))
    return redirect('catalog:product_detail', slug=product.slug)


@login_required
def my_reviews_view(request):
    reviews = Review.objects.filter(user=request.user).select_related('product')
    reviewed_ids = reviews.values_list('product_id', flat=True)
    eligible_products = Product.objects.filter(
        order_items__order__user=request.user,
        order_items__order__order_status=Order.OrderStatus.DELIVERED,
    ).exclude(pk__in=reviewed_ids).distinct()
    return render(request, 'accounts/reviews.html', {'reviews': reviews, 'eligible_products': eligible_products})
