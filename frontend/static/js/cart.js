/**
 * SoundSphere Shopping Cart AJAX Controller
 * Handles add to cart, instant quantity updates, removal, and live calculations
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Add to Cart from any button across the site
  const cartSelectors = '.add-to-cart-btn, .btn-add-to-cart, .btn-card-cart, .add-to-cart-btn-lg';
  
  document.querySelectorAll(cartSelectors).forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const productId = btn.getAttribute('data-product-id');
      if (!productId) return;

      const qtyInput = document.getElementById('product-qty') || document.getElementById('detail-qty-input');
      const quantity = qtyInput ? Math.max(1, parseInt(qtyInput.value || '1', 10)) : 1;

      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `
        <svg class="spin-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 0.7s linear infinite; display: inline-block; vertical-align: middle; margin-right: 4px;">
          <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
          <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
        </svg>
        Adding...
      `;

      try {
        const res = await SoundSphere.fetchAPI('/api/cart/add/', {
          method: 'POST',
          body: JSON.stringify({ product_id: productId, quantity: quantity })
        });

        if (res.ok) {
          btn.innerHTML = `✓ Added to Cart!`;
          btn.style.background = 'var(--color-success)';
          btn.style.borderColor = 'var(--color-success)';

          if (window.SoundSphere && typeof SoundSphere.toast === 'function') {
            SoundSphere.toast(res.data.message || 'Product added to cart!', 'success');
            SoundSphere.updateCounters({ cart_count: res.data.cart_count });
          }

          setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.style.borderColor = '';
          }, 1600);
        } else {
          btn.disabled = false;
          btn.innerHTML = originalText;
          const errMsg = res.data.error || res.data.message || 'Could not add product to cart.';
          if (window.SoundSphere && typeof SoundSphere.toast === 'function') {
            SoundSphere.toast(errMsg, 'error');
          }
        }
      } catch (err) {
        btn.disabled = false;
        btn.innerHTML = originalText;
        console.error('Cart add error:', err);
      }
    });
  });

  // 2. Buy Now Button (Adds to cart & redirects immediately to /orders/checkout/)
  const btnBuyNow = document.getElementById('btn-buy-now');
  if (btnBuyNow) {
    btnBuyNow.addEventListener('click', async (e) => {
      e.preventDefault();
      const productId = btnBuyNow.getAttribute('data-product-id');
      const qtyInput = document.getElementById('product-qty') || document.getElementById('detail-qty-input');
      const quantity = qtyInput ? Math.max(1, parseInt(qtyInput.value || '1', 10)) : 1;

      if (!productId) return;

      btnBuyNow.disabled = true;
      btnBuyNow.textContent = 'Securing Checkout...';

      const res = await SoundSphere.fetchAPI('/api/cart/add/', {
        method: 'POST',
        body: JSON.stringify({ product_id: productId, quantity: quantity })
      });

      if (res.ok) {
        window.location.href = '/orders/checkout/';
      } else {
        btnBuyNow.disabled = false;
        btnBuyNow.textContent = 'Buy Now';
        SoundSphere.toast(res.data.error || 'Could not proceed to checkout.', 'error');
      }
    });
  }
});
