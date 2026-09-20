from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm
from .models import Address, UserProfile
from apps.orders.models import Order
from apps.wishlist.models import Wishlist
from apps.cart.models import Cart, CartItem
from apps.reviews.models import Review


def merge_guest_cart_into_user_cart(request, user):
    """Transfers guest session cart items into the user's permanent account cart upon login."""
    session_key = request.session.session_key
    if not session_key:
        return

    guest_cart = Cart.objects.filter(session_key=session_key).first()
    if not guest_cart or not guest_cart.items.exists():
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for g_item in guest_cart.items.all():
        u_item = CartItem.objects.filter(cart=user_cart, product=g_item.product).first()
        if u_item:
            # Check stock limit
            new_qty = min(u_item.quantity + g_item.quantity, g_item.product.stock_quantity)
            u_item.quantity = new_qty
            u_item.save(update_fields=['quantity'])
        else:
            g_item.cart = user_cart
            g_item.save(update_fields=['cart'])

    guest_cart.delete()


def register_view(request):
    """Handles new user registration."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Wishlist.objects.get_or_create(user=user)
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
            merge_guest_cart_into_user_cart(request, user)
            messages.success(request, _('Welcome to SoundSphere! Your account was created successfully.'))
            next_url = request.GET.get('next') or 'accounts:profile'
            return redirect(next_url)
        else:
            messages.error(request, _('Please correct the errors below to complete your registration.'))
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handles user login with email/username."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    redirect_to = request.GET.get('next', 'accounts:profile')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Remember me cookie lifetime
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0) # Browser close
            else:
                request.session.set_expiry(30 * 24 * 60 * 60) # 30 days
                
            merge_guest_cart_into_user_cart(request, user)
            messages.success(request, _(f"Welcome back, {user.first_name or user.username}!"))
            return redirect(redirect_to)
        else:
            messages.error(request, _('Invalid login credentials.'))
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': redirect_to})


def logout_view(request):
    """Logs out user and redirects to homepage."""
    logout(request)
    messages.info(request, _('You have been safely logged out.'))
    return redirect('core:home')


@login_required
def profile_view(request):
    """Displays user profile, account metrics, and recent orders."""
    user = request.user
    recent_orders = Order.objects.filter(user=user).prefetch_related('items')[:5]
    total_orders = Order.objects.filter(user=user).count()
    pending_orders = Order.objects.filter(user=user, order_status=Order.OrderStatus.PENDING).count()
    delivered_orders = Order.objects.filter(user=user, order_status=Order.OrderStatus.DELIVERED).count()
    total_spent = Order.objects.filter(user=user).exclude(
        order_status=Order.OrderStatus.CANCELLED
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    saved_addresses = Address.objects.filter(user=user)
    wishlist = Wishlist.objects.filter(user=user).first()
    reviewed_product_ids = Review.objects.filter(user=user).values_list('product_id', flat=True)
    eligible_reviews = Order.objects.filter(
        user=user, order_status=Order.OrderStatus.DELIVERED
    ).values_list('items__product_id', flat=True).distinct()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated successfully.'))
            return redirect('accounts:profile')
        else:
            messages.error(request, _('Please correct the errors in the profile form.'))
    else:
        form = UserProfileForm(instance=user)

    context = {
        'form': form,
        'user': user,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_spent': total_spent,
        'saved_addresses': saved_addresses,
        'wishlist_count': wishlist.items.count() if wishlist else 0,
        'eligible_review_count': eligible_reviews.exclude(pk__in=reviewed_product_ids).count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def addresses_view(request, pk=None):
    """Lists saved addresses and handles ownership-scoped create/edit submission."""
    addresses = Address.objects.filter(user=request.user)
    address = get_object_or_404(addresses, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            saved_address = form.save(commit=False)
            saved_address.user = request.user
            saved_address.save()
            messages.success(request, _('Address updated successfully.') if address else _('New address saved successfully.'))
            return redirect('accounts:addresses')
        else:
            messages.error(request, _('Please correct the address form errors.'))
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/addresses.html', {'addresses': addresses, 'form': form, 'editing_address': address})


@login_required
def address_delete_view(request, pk):
    """Deletes an address belonging to the authenticated user."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, _('Address deleted successfully.'))
    return redirect('accounts:addresses')


@login_required
def address_set_default_view(request, pk):
    """Sets the chosen address as default for the user."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        Address.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
        address.save(update_fields=['is_default'])
        messages.success(request, _('Default address updated.'))
    return redirect('accounts:addresses')


@login_required
def password_change_view(request):
    """Allows user to change password securely."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Your password has been changed successfully.'))
            return redirect('accounts:profile')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})
