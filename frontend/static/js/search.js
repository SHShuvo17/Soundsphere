/**
 * SoundSphere Instant Live Search with Keyboard Navigation & Autocomplete
 */

document.addEventListener('DOMContentLoaded', () => {
  setupSearchInput('search-input', 'search-dropdown');
  setupSearchInput('mobile-search-input', null);

  function setupSearchInput(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = dropdownId ? document.getElementById(dropdownId) : null;
    let debounceTimeout = null;
    let activeIndex = -1;

    if (!input) return;

    // Handle Enter key on input to submit standard search
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const query = input.value.trim();
        if (query) {
          window.location.href = `/shop/?search=${encodeURIComponent(query)}`;
        }
      }

      if (!dropdown || !dropdown.classList.contains('show')) return;

      const items = dropdown.querySelectorAll('.search-item');
      if (items.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = (activeIndex + 1) % items.length;
        updateActiveItem(items, activeIndex);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = (activeIndex - 1 + items.length) % items.length;
        updateActiveItem(items, activeIndex);
      } else if (e.key === 'Escape') {
        dropdown.classList.remove('show');
      }
    });

    function updateActiveItem(items, index) {
      items.forEach((item, i) => {
        if (i === index) {
          item.style.background = 'var(--bg-card-hover)';
          item.focus();
        } else {
          item.style.background = '';
        }
      });
    }

    if (!dropdown) return;

    input.addEventListener('input', (e) => {
      const query = e.target.value.trim();
      clearTimeout(debounceTimeout);
      activeIndex = -1;

      if (query.length < 2) {
        dropdown.classList.remove('show');
        dropdown.innerHTML = '';
        return;
      }

      debounceTimeout = setTimeout(async () => {
        try {
          const response = await fetch(`/api/products/?search=${encodeURIComponent(query)}`);
          const data = await response.json();
          const results = data.results || (Array.isArray(data) ? data : []);

          if (results.length === 0) {
            dropdown.innerHTML = `
              <div style="padding: 1.25rem; text-align: center; color: var(--text-muted); font-size: 0.88rem;">
                No audio products found for "<strong>${escapeHtml(query)}</strong>"
              </div>
            `;
            dropdown.classList.add('show');
            return;
          }

          let html = '';
          results.slice(0, 5).forEach(product => {
            const imgUrl = product.primary_image ? product.primary_image.url : '/static/images/placeholder-speaker.svg';
            const price = product.discount_price || product.price;
            html += `
              <a href="/product/${product.slug}/" class="search-item" tabindex="-1">
                <img src="${imgUrl}" alt="${escapeHtml(product.name)}" class="search-item-img">
                <div class="search-item-info">
                  <div class="search-item-name">${escapeHtml(product.name)}</div>
                  <div class="search-item-brand">${escapeHtml(product.brand ? product.brand.name : '')}</div>
                </div>
                <div class="search-item-price">$${parseFloat(price).toFixed(2)}</div>
              </a>
            `;
          });

          html += `
            <a href="/shop/?search=${encodeURIComponent(query)}" style="display: block; padding: 0.75rem 1rem; text-align: center; font-size: 0.82rem; font-weight: 700; color: var(--color-primary); background: var(--bg-surface); text-decoration: none; border-top: 1px solid var(--border-subtle);">
              View All Results for "${escapeHtml(query)}" →
            </a>
          `;

          dropdown.innerHTML = html;
          dropdown.classList.add('show');
        } catch (err) {
          console.error('Search fetch error:', err);
        }
      }, 250);
    });

    // Hide dropdown on click outside
    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });

    input.addEventListener('focus', () => {
      if (input.value.trim().length >= 2 && dropdown.children.length > 0) {
        dropdown.classList.add('show');
      }
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[m]));
  }
});
