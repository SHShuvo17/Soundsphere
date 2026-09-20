from decimal import Decimal
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, OrderItem
from apps.catalog.models import Product, Category, Brand, ProductType
from apps.accounts.models import User
from apps.reviews.models import Review
from apps.promotions.models import Coupon
from .forms import StaffProductForm, StaffCategoryForm, StaffProductTypeForm, StaffBrandForm, StaffCouponForm


@staff_member_required(login_url='accounts:login')
def admin_dashboard_view(request):
    """Admin operational & executive business dashboard with revenue charts and KPI metrics."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    # 1. High-Level KPIs
    total_revenue = Order.objects.filter(
        payment_status=Order.PaymentStatus.PAID
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status=Order.OrderStatus.PENDING).count()
    total_customers = User.objects.filter(is_staff=False).count()
    active_products = Product.objects.filter(is_active=True).count()

    # 2. Recent 30 Days Revenue
    recent_revenue = Order.objects.filter(
        payment_status=Order.PaymentStatus.PAID,
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # 3. Low Stock Alerts
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=5
    ).order_by('stock_quantity')[:8]

    # 4. Recent Orders
    recent_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')[:10]

    # 5. Order Status Breakdown
    status_counts = Order.objects.values('order_status').annotate(count=Count('id'))
    status_breakdown = {s['order_status']: s['count'] for s in status_counts}

    # 6. Pending Reviews
    pending_reviews_count = Review.objects.filter(is_approved=False).count()

    context = {
        'total_revenue': total_revenue,
        'recent_revenue': recent_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'status_breakdown': status_breakdown,
        'pending_reviews_count': pending_reviews_count,
    }
    return render(request, 'dashboard/index.html', context)


@staff_member_required(login_url='accounts:login')
def admin_orders_view(request):
    """Lists customer orders for staff with search and status filtering."""
    orders = Order.objects.select_related('user').prefetch_related('items', 'payment').order_by('-created_at')
    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()

    if search:
        orders = orders.filter(
            Q(order_number__icontains=search)
            | Q(user__email__icontains=search)
            | Q(user__username__icontains=search)
        )
    if status in dict(Order.OrderStatus.choices):
        orders = orders.filter(order_status=status)
    if payment_status in dict(Order.PaymentStatus.choices):
        orders = orders.filter(payment_status=payment_status)

    context = {
        'orders': orders,
        'search': search,
        'selected_status': status,
        'selected_payment_status': payment_status,
        'order_statuses': Order.OrderStatus.choices,
        'payment_statuses': Order.PaymentStatus.choices,
    }
    return render(request, 'dashboard/orders.html', context)


@staff_member_required(login_url='accounts:login')
def admin_order_status_view(request, order_number):
    """Updates fulfillment status from the staff order workspace."""
    order = get_object_or_404(Order, order_number=order_number)
    if request.method != 'POST':
        return redirect('dashboard:orders')
    new_status = request.POST.get('order_status', '')
    new_payment_status = request.POST.get('payment_status', order.payment_status)
    valid_statuses = dict(Order.OrderStatus.choices)

    if new_status in valid_statuses and new_payment_status in dict(Order.PaymentStatus.choices):
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            order.order_status = new_status
            order.payment_status = new_payment_status
            order.save(update_fields=['order_status', 'payment_status', 'updated_at'])
            if hasattr(order, 'payment'):
                order.payment.status = order.payment_status
                order.payment.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Order #{order.order_number} updated to {valid_statuses[new_status]}.')
    else:
        messages.error(request, 'Choose a valid order status.')

    return redirect(request.POST.get('next') or 'dashboard:orders')


@staff_member_required(login_url='accounts:login')
def admin_order_detail_view(request, order_number):
    order = get_object_or_404(Order.objects.select_related('user', 'payment', 'shipping_detail').prefetch_related('items'), order_number=order_number)
    return render(request, 'dashboard/order_detail.html', {'order': order, 'order_statuses': Order.OrderStatus.choices, 'payment_statuses': Order.PaymentStatus.choices})


RESOURCE_CONFIG = {
    'products': (Product, StaffProductForm, 'Products', ('name', 'sku', 'brand__name')),
    'categories': (Category, StaffCategoryForm, 'Categories', ('name',)),
    'product-types': (ProductType, StaffProductTypeForm, 'Product Types', ('name', 'category__name')),
    'brands': (Brand, StaffBrandForm, 'Brands', ('name',)),
    'coupons': (Coupon, StaffCouponForm, 'Coupons', ('code',)),
}


@staff_member_required(login_url='accounts:login')
def admin_resource_list_view(request, resource):
    model, _, label, search_fields = RESOURCE_CONFIG[resource]
    objects = model.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        filters = Q()
        for field in search_fields:
            filters |= Q(**{f'{field}__icontains': query})
        objects = objects.filter(filters)
    return render(request, 'dashboard/manage_list.html', {'objects': objects, 'resource': resource, 'label': label, 'search': query})


@staff_member_required(login_url='accounts:login')
def admin_resource_form_view(request, resource, pk=None):
    model, form_class, label, _ = RESOURCE_CONFIG[resource]
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{label[:-1] if label.endswith("s") else label} saved.')
        return redirect('dashboard:resource_list', resource=resource)
    return render(request, 'dashboard/manage_form.html', {'form': form, 'resource': resource, 'label': label, 'object': instance})


@staff_member_required(login_url='accounts:login')
def admin_resource_delete_view(request, resource, pk):
    model, _, label, _ = RESOURCE_CONFIG[resource]
    if request.method == 'POST':
        get_object_or_404(model, pk=pk).delete()
        messages.success(request, f'{label[:-1] if label.endswith("s") else label} deleted.')
    return redirect('dashboard:resource_list', resource=resource)


@staff_member_required(login_url='accounts:login')
def admin_customers_view(request):
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')
    query = request.GET.get('q', '').strip()
    if query:
        customers = customers.filter(Q(email__icontains=query) | Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    return render(request, 'dashboard/customers.html', {'customers': customers, 'search': query})


@staff_member_required(login_url='accounts:login')
def admin_customer_toggle_view(request, pk):
    if request.method == 'POST':
        customer = get_object_or_404(User, pk=pk, is_staff=False)
        customer.is_active = not customer.is_active
        customer.save(update_fields=['is_active'])
        messages.success(request, 'Customer status updated.')
    return redirect('dashboard:customers')


@staff_member_required(login_url='accounts:login')
def admin_reviews_view(request):
    reviews = Review.objects.select_related('user', 'product')
    if request.GET.get('status') == 'pending':
        reviews = reviews.filter(is_approved=False)
    return render(request, 'dashboard/reviews.html', {'reviews': reviews})


@staff_member_required(login_url='accounts:login')
def admin_review_action_view(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            review.delete()
        else:
            review.is_approved = request.POST.get('action') == 'approve'
            review.save(update_fields=['is_approved', 'updated_at'])
        messages.success(request, 'Review moderation updated.')
    return redirect('dashboard:reviews')


@staff_member_required(login_url='accounts:login')
def admin_reports_view(request):
    """Provides staff with safe, downloadable customer data reports."""
    customer_count = User.objects.filter(is_staff=False).count()
    return render(request, 'dashboard/reports.html', {'customer_count': customer_count})


@staff_member_required(login_url='accounts:login')
def admin_users_csv_view(request):
    """Exports non-sensitive customer data as a CSV download for staff."""
    customers = User.objects.filter(is_staff=False).annotate(
        order_count=Count('orders', distinct=True),
        total_spent=Sum('orders__total_amount'),
    ).order_by('-date_joined')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="soundsphere-customers.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow([
        'User ID', 'First Name', 'Last Name', 'Username', 'Email', 'Phone',
        'Date Joined', 'Active', 'Order Count', 'Total Spent',
    ])

    for customer in customers:
        writer.writerow([
            customer.pk,
            customer.first_name,
            customer.last_name,
            customer.username,
            customer.email,
            customer.phone,
            customer.date_joined.isoformat(),
            'Yes' if customer.is_active else 'No',
            customer.order_count,
            f'{customer.total_spent or Decimal("0.00"):.2f}',
        ])

    return response
