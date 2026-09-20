from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Min, Max
from .models import Category, ProductType, Brand, Product
from apps.reviews.models import Review
from apps.orders.models import Order


def shop_view(request):
    """Full filterable, searchable, sortable shop catalog with backend pagination."""
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category', 'product_type').prefetch_related('images')
    
    # 1. Search Query
    search = request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(category__name__icontains=search) |
            Q(product_type__name__icontains=search) |
            Q(short_description__icontains=search)
        )

    # 2. Category Filter
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        queryset = queryset.filter(category__slug__in=selected_categories)

    # 3. Product Type Filter
    selected_types = request.GET.getlist('type')
    if selected_types:
        queryset = queryset.filter(product_type__slug__in=selected_types)

    # 4. Brand Filter
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        queryset = queryset.filter(brand__slug__in=selected_brands)

    # 5. Price Filter
    max_price = request.GET.get('max_price')
    if max_price:
        try:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    # 6. Stock Filter
    in_stock = request.GET.get('in_stock')
    if in_stock in ['true', '1']:
        queryset = queryset.filter(stock_quantity__gt=0)

    # 7. Rating Filter
    min_rating = request.GET.get('rating')
    if min_rating:
        try:
            queryset = queryset.filter(rating__gte=Decimal(min_rating))
        except Exception:
            pass

    # 8. Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        queryset = queryset.order_by('price')
    elif sort == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort == 'rating':
        queryset = queryset.order_by('-rating')
    elif sort == 'popular':
        queryset = queryset.order_by('-sold_count')
    else:
        queryset = queryset.order_by('-created_at')

    # Pagination
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Filter metadata
    categories = Category.objects.filter(is_active=True).annotate(prod_count=Count('products', filter=Q(products__is_active=True)))
    product_types = ProductType.objects.filter(is_active=True).annotate(prod_count=Count('products', filter=Q(products__is_active=True)))
    brands = Brand.objects.filter(is_active=True).annotate(prod_count=Count('products', filter=Q(products__is_active=True)))

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
        'categories': categories,
        'product_types': product_types,
        'brands': brands,
        'selected_categories': selected_categories,
        'selected_types': selected_types,
        'selected_brands': selected_brands,
        'search': search,
        'sort': sort,
        'max_price': max_price or '1500',
        'in_stock': in_stock,
        'min_rating': min_rating,
    }
    return render(request, 'shop.html', context)


def category_view(request, slug):
    """Category landing view with product type filter chips and products."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    product_types = category.product_types.filter(is_active=True)
    products = Product.objects.filter(category=category, is_active=True).select_related('brand', 'product_type').prefetch_related('images')
    
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'category': category,
        'product_types': product_types,
        'products': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
    }
    return render(request, 'category.html', context)


def product_type_view(request, slug):
    """Product Type landing view for specific subcategory."""
    product_type = get_object_or_404(ProductType, slug=slug, is_active=True)
    products = Product.objects.filter(product_type=product_type, is_active=True).select_related('brand', 'category').prefetch_related('images')
    
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'product_type': product_type,
        'category': product_type.category,
        'products': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
    }
    return render(request, 'product_type.html', context)


def product_detail_view(request, slug):
    """Single product showcase with interactive gallery, specifications, and customer reviews."""
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category', 'product_type')
        .prefetch_related('images', 'specifications'),
        slug=slug,
        is_active=True
    )
    
    reviews = Review.objects.filter(product=product, is_approved=True).select_related('user')
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id).select_related('brand').prefetch_related('images')[:4]

    # Calculate rating distribution (5, 4, 3, 2, 1 stars)
    rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        if r.rating in rating_distribution:
            rating_distribution[r.rating] += 1

    # Check if user can submit a review
    user_can_review = False
    is_verified_buyer = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(user=request.user, product=product).exists()
        if not user_has_reviewed:
            is_verified_buyer = Order.objects.filter(
                user=request.user,
                order_status=Order.OrderStatus.DELIVERED,
                items__product=product
            ).exists()
            user_can_review = is_verified_buyer

    context = {
        'product': product,
        'images': product.images.all(),
        'specifications': product.specifications.all(),
        'reviews': reviews,
        'related_products': related_products,
        'rating_distribution': rating_distribution,
        'user_can_review': user_can_review,
        'is_verified_buyer': is_verified_buyer,
    }
    return render(request, 'product_detail.html', context)


def brands_view(request):
    """Brand directory page showcasing all audio manufacturers."""
    brands = Brand.objects.filter(is_active=True).annotate(prod_count=Count('products', filter=Q(products__is_active=True)))
    return render(request, 'brands.html', {'brands': brands})
