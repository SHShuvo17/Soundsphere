/**
 * SoundSphere Product Detail Interactive Controller
 * Image gallery switching, zoom, quantity controls, spec tabs
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Gallery Thumbnail Switching
  const mainImg = document.getElementById('detail-main-img');
  const thumbs = document.querySelectorAll('.thumb-item');

  thumbs.forEach(thumb => {
    thumb.addEventListener('click', () => {
      thumbs.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      const targetUrl = thumb.getAttribute('data-img-url');
      if (mainImg && targetUrl) {
        mainImg.style.opacity = '0.3';
        setTimeout(() => {
          mainImg.src = targetUrl;
          mainImg.style.opacity = '1';
        }, 150);
      }
    });
  });

  // 2. Quantity Selector
  const qtyInput = document.getElementById('detail-qty-input');
  const btnPlus = document.getElementById('detail-qty-plus');
  const btnMinus = document.getElementById('detail-qty-minus');

  if (qtyInput) {
    const maxStock = parseInt(qtyInput.getAttribute('max') || '99', 10);
    const minQty = parseInt(qtyInput.getAttribute('min') || '1', 10);

    if (btnPlus) {
      btnPlus.addEventListener('click', () => {
        let current = parseInt(qtyInput.value || '1', 10);
        if (current < maxStock) {
          qtyInput.value = current + 1;
        } else {
          SoundSphere.toast(`Only ${maxStock} items available in stock`, 'info', 2000);
        }
      });
    }

    if (btnMinus) {
      btnMinus.addEventListener('click', () => {
        let current = parseInt(qtyInput.value || '1', 10);
        if (current > minQty) {
          qtyInput.value = current - 1;
        }
      });
    }

    qtyInput.addEventListener('change', () => {
      let val = parseInt(qtyInput.value, 10);
      if (isNaN(val) || val < minQty) val = minQty;
      if (val > maxStock) {
        val = maxStock;
        SoundSphere.toast(`Clamped to maximum available stock (${maxStock})`, 'info');
      }
      qtyInput.value = val;
    });
  }

  // 3. Product Tabs (Description, Specifications, Reviews)
  const tabBtns = document.querySelectorAll('.tab-nav-btn');
  const tabPanels = document.querySelectorAll('.tab-content-panel');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab-target');

      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }
    });
  });
});
