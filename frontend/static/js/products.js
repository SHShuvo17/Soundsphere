/**
 * SoundSphere Shop Catalog Filtering & Sorting
 */

document.addEventListener('DOMContentLoaded', () => {
  const filterForm = document.getElementById('shop-filter-form');
  const sortSelect = document.getElementById('shop-sort-select');
  const priceSlider = document.getElementById('price-range-slider');
  const priceDisplay = document.getElementById('price-max-display');

  if (priceSlider && priceDisplay) {
    priceSlider.addEventListener('input', (e) => {
      priceDisplay.textContent = `$${e.target.value}`;
    });
    priceSlider.addEventListener('change', () => {
      if (filterForm) filterForm.submit();
    });
  }

  if (sortSelect && filterForm) {
    sortSelect.addEventListener('change', () => {
      const hiddenSort = document.getElementById('hidden-sort-input');
      if (hiddenSort) {
        hiddenSort.value = sortSelect.value;
      }
      filterForm.submit();
    });
  }

  // Auto submit when checkbox filters change
  const autoCheckboxes = document.querySelectorAll('.auto-filter-check');
  autoCheckboxes.forEach(chk => {
    chk.addEventListener('change', () => {
      if (filterForm) filterForm.submit();
    });
  });
});
