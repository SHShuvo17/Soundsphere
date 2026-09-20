/**
 * SoundSphere Core JavaScript
 * Global utilities, CSRF handling, toast notifications, dynamic badge counters
 */

window.SoundSphere = window.SoundSphere || {};

// Retrieve CSRF token from cookie, meta tag, or DOM input
SoundSphere.getCSRFToken = function() {
  const match = document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'));
  if (match) return match[2];
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute('content');
  const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return input ? input.value : '';
};

// Global Toast Notification System with Icons and Auto Dismiss
SoundSphere.toast = function(message, type = 'success', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toast.innerHTML = `
    <span style="font-weight: 800; font-size: 1.15rem; color: var(--${type === 'success' ? 'color-success' : type === 'error' ? 'color-error' : 'color-primary'});">${icon}</span>
    <span style="flex: 1; font-weight: 500;">${message}</span>
    <button class="toast-close" aria-label="Dismiss">&times;</button>
  `;

  const closeBtn = toast.querySelector('.toast-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 250);
    });
  }

  container.appendChild(toast);

  // Trigger smooth enter animation
  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  // Auto remove timer
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
};

// Live Update Badge Counters on Navbar
SoundSphere.updateCounters = function(data) {
  if (data.cart_count !== undefined) {
    const cartBadges = document.querySelectorAll('#cart-count, .cart-count-badge, .cart-badge');
    cartBadges.forEach(el => {
      el.textContent = data.cart_count;
      el.style.display = data.cart_count > 0 ? 'flex' : 'none';
      el.style.animation = 'none';
      requestAnimationFrame(() => {
        el.style.animation = 'badge-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
      });
    });
  }

  if (data.wishlist_count !== undefined) {
    const wishBadges = document.querySelectorAll('#wishlist-count, .wishlist-count-badge, .wishlist-badge');
    wishBadges.forEach(el => {
      el.textContent = data.wishlist_count;
      el.style.display = data.wishlist_count > 0 ? 'flex' : 'none';
      el.style.animation = 'none';
      requestAnimationFrame(() => {
        el.style.animation = 'badge-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
      });
    });
  }
};

// Helper for authenticated Fetch API requests
SoundSphere.fetchAPI = async function(url, options = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'X-CSRFToken': SoundSphere.getCSRFToken(),
  };

  options.headers = { ...defaultHeaders, ...options.headers };

  try {
    const response = await fetch(url, options);
    const data = await response.json();
    return { ok: response.ok, status: response.status, data };
  } catch (error) {
    console.error('SoundSphere API Error:', error);
    return { ok: false, status: 500, data: { message: 'Network connection error. Please try again.' } };
  }
};

// Common DOM initialization
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss standard alerts if any
  document.querySelectorAll('.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    }, 4000);
  });
});
