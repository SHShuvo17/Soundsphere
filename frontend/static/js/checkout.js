/**
 * SoundSphere Checkout Controller
 * Address selection, live coupon validation, atomic order submission
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Saved Address vs New Address Toggle
  const addressRadios = document.querySelectorAll('input[name="shipping_address_choice"]');
  const newAddressForm = document.getElementById('new-address-collapse');

  addressRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      if (radio.value === 'new') {
        if (newAddressForm) newAddressForm.style.display = 'block';
      } else {
        if (newAddressForm) newAddressForm.style.display = 'none';
      }
    });
  });

  // 2. Coupon Application
  const btnApplyCoupon = document.getElementById('btn-apply-coupon');
  const couponInput = document.getElementById('coupon-code-input');
  const couponFeedback = document.getElementById('coupon-feedback');
  const hiddenCouponCode = document.getElementById('hidden-coupon-code');

  if (btnApplyCoupon && couponInput) {
    btnApplyCoupon.addEventListener('click', async (e) => {
      e.preventDefault();
      const code = couponInput.value.trim().toUpperCase();
      if (!code) {
        SoundSphere.toast('Please enter a coupon code.', 'info');
        return;
      }

      btnApplyCoupon.disabled = true;
      btnApplyCoupon.textContent = 'Verifying...';

      const res = await SoundSphere.fetchAPI('/api/coupons/validate/', {
        method: 'POST',
        body: JSON.stringify({ code: code })
      });

      btnApplyCoupon.disabled = false;
      btnApplyCoupon.textContent = 'Apply';

      if (res.ok && res.data.is_valid) {
        if (hiddenCouponCode) hiddenCouponCode.value = code;
        
        // Update summary rows
        const discountRow = document.getElementById('summary-discount-row');
        const discountVal = document.getElementById('summary-discount-val');
        const totalVal = document.getElementById('summary-total-val');

        if (discountRow) discountRow.style.display = 'flex';
        if (discountVal) discountVal.textContent = `-$${parseFloat(res.data.discount_amount).toFixed(2)}`;
        if (totalVal) totalVal.textContent = `$${parseFloat(res.data.new_total).toFixed(2)}`;

        if (couponFeedback) {
          couponFeedback.innerHTML = `<span style="color: var(--accent-green); font-size: 0.85rem; font-weight: 700;">✓ Coupon "${code}" Applied: $${parseFloat(res.data.discount_amount).toFixed(2)} OFF</span>`;
        }
        SoundSphere.toast(res.data.message || 'Coupon applied successfully!', 'success');
      } else {
        if (couponFeedback) {
          couponFeedback.innerHTML = `<span style="color: var(--accent-red); font-size: 0.85rem;">✕ ${res.data.error || 'Invalid coupon code.'}</span>`;
        }
        SoundSphere.toast(res.data.error || 'Invalid coupon code.', 'error');
      }
    });
  }

  // 3. Checkout Form Submission Guard
  const checkoutForm = document.getElementById('checkout-form');
  const btnPlaceOrder = document.getElementById('btn-place-order');

  if (checkoutForm && btnPlaceOrder) {
    checkoutForm.addEventListener('submit', (e) => {
      btnPlaceOrder.disabled = true;
      btnPlaceOrder.innerHTML = `
        <span class="spinner" style="display: inline-block; width: 18px; height: 18px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; margin-right: 8px;"></span>
        Securing Order & Reserving Stock...
      `;
    });
  }
});
