/**
 * SoundSphere Customer Review & Rating Interactive System
 */

document.addEventListener('DOMContentLoaded', () => {
  const starIcons = document.querySelectorAll('.star-picker-icon');
  const ratingInput = document.getElementById('review-rating-val');

  if (starIcons.length > 0 && ratingInput) {
    starIcons.forEach(star => {
      star.addEventListener('mouseenter', () => {
        const val = parseInt(star.getAttribute('data-value'), 10);
        highlightStars(val);
      });

      star.addEventListener('click', () => {
        const val = parseInt(star.getAttribute('data-value'), 10);
        ratingInput.value = val;
        setSelectedStars(val);
      });
    });

    const starContainer = document.getElementById('star-picker-container');
    if (starContainer) {
      starContainer.addEventListener('mouseleave', () => {
        const currentSelected = parseInt(ratingInput.value || '5', 10);
        setSelectedStars(currentSelected);
      });
    }

    function highlightStars(val) {
      starIcons.forEach(s => {
        const sVal = parseInt(s.getAttribute('data-value'), 10);
        s.style.color = sVal <= val ? '#ffb300' : '#4b5563';
      });
    }

    function setSelectedStars(val) {
      highlightStars(val);
    }

    // Default select 5 stars
    setSelectedStars(5);
  }

  // Review Modal Toggle
  const openReviewBtn = document.getElementById('btn-open-review-modal');
  const reviewModal = document.getElementById('review-modal');
  const closeReviewBtn = document.getElementById('btn-close-review-modal');

  if (openReviewBtn && reviewModal) {
    openReviewBtn.addEventListener('click', () => {
      reviewModal.style.display = 'flex';
    });
  }

  if (closeReviewBtn && reviewModal) {
    closeReviewBtn.addEventListener('click', () => {
      reviewModal.style.display = 'none';
    });
  }

  if (reviewModal) {
    reviewModal.addEventListener('click', (e) => {
      if (e.target === reviewModal) reviewModal.style.display = 'none';
    });
  }
});
