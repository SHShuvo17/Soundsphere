from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from .models import ContactMessage, NewsletterSubscriber
from apps.catalog.models import Category, ProductType, Product
from apps.promotions.models import Banner
from apps.reviews.models import Review


def home_view(request):
    """SoundSphere rich homepage showcase."""
    featured_categories = Category.objects.filter(is_active=True).prefetch_related('product_types')[:8]
    popular_types = ProductType.objects.filter(is_active=True).select_related('category')[:12]
    
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related('brand', 'category').prefetch_related('images')[:8]
    best_sellers = Product.objects.filter(is_active=True, is_best_seller=True).select_related('brand', 'category').prefetch_related('images')[:8]
    new_arrivals = Product.objects.filter(is_active=True, is_new_arrival=True).select_related('brand', 'category').prefetch_related('images')[:8]
    
    banners = Banner.objects.filter(is_active=True).order_by('display_order')[:2]
    customer_reviews = Review.objects.filter(is_approved=True, rating__gte=4).select_related('user', 'product')[:6]

    context = {
        'featured_categories': featured_categories,
        'popular_types': popular_types,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
        'banners': banners,
        'customer_reviews': customer_reviews,
    }
    return render(request, 'home.html', context)


def about_view(request):
    """About SoundSphere brand, engineering heritage, and quality standards."""
    return render(request, 'core/about.html')


def contact_view(request):
    """Customer support inquiry form."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, _('Thank you for reaching out! Our audio support team will get back to you within 24 hours.'))
            return redirect('core:contact')
        else:
            messages.error(request, _('Please complete all required fields.'))

    return render(request, 'core/contact.html')


def newsletter_subscribe_view(request):
    """Newsletter subscription handler."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if email:
            sub, created = NewsletterSubscriber.objects.get_or_create(email=email, defaults={'is_active': True})
            if created:
                msg = _('Thank you for subscribing to SoundSphere Audio Dispatch!')
            else:
                msg = _('You are already subscribed to our newsletter.')
                
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'status': 'ok', 'message': msg})
            messages.success(request, msg)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Invalid email address.'}, status=400)
            messages.error(request, _('Please provide a valid email address.'))
            
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


def error_404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_403_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_500_view(request):
    return render(request, 'errors/500.html', status=500)
