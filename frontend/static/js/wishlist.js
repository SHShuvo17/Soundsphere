/**
 * SoundSphere Customer Wishlist AJAX Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const wishlistSelectors = '.wishlist-toggle-btn, .btn-wishlist, .btn-detail-wishlist, .wishlist-toggle-lg';

  document.querySelectorAll(wishlistSelectors).forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const productId = btn.getAttribute('data-product-id');
      if (!productId) return;

      const isDetailBtn = btn.classList.contains('wishlist-toggle-lg') || btn.classList.contains('btn-detail-wishlist');

      try {
        const res = await SoundSphere.fetchAPI('/api/wishlist/toggle/', {
          method: 'POST',
          body: JSON.stringify({ product_id: productId })
        });

        if (res.status === 401 || (res.data && res.data.redirect)) {
          SoundSphere.toast('Please sign in to save items to your wishlist.', 'info');
          setTimeout(() => {
            window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
          }, 1000);
          return;
        }

        if (res.ok) {
          if (res.data.action === 'added') {
            btn.classList.add('active');
            btn.style.color = 'var(--accent-pink)';
            btn.style.borderColor = 'var(--accent-pink)';
            if (isDetailBtn) {
              btn.innerHTML = `<span style="color:var(--accent-pink)">♥</span> Saved in Wishlist`;
            }
            SoundSphere.toast(res.data.message || 'Saved to your wishlist!', 'success');
          } else {
            btn.classList.remove('active');
            btn.style.color = '';
            btn.style.borderColor = '';
            if (isDetailBtn) {
              btn.innerHTML = `♡ Add to Wishlist`;
            }
            SoundSphere.toast(res.data.message || 'Removed from wishlist.', 'info');
          }

          if (res.data.wishlist_count !== undefined) {
            SoundSphere.updateCounters({ wishlist_count: res.data.wishlist_count });
          }
        } else {
          SoundSphere.toast(res.data.error || 'Could not update wishlist.', 'error');
        }
      } catch (err) {
        console.error('Wishlist toggle error:', err);
      }
    });
  });
});
