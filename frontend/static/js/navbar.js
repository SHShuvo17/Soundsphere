/**
 * SoundSphere Navbar, Header Scroll Effects & Mobile Drawer Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.getElementById('hamburger') || document.getElementById('mobile-drawer-toggle');
  const drawer = document.getElementById('mobile-drawer');
  const overlay = document.getElementById('mobile-overlay') || document.getElementById('mobile-drawer-overlay');
  const drawerClose = document.getElementById('drawer-close') || document.getElementById('mobile-drawer-close');
  const header = document.getElementById('site-header');

  function openDrawer() {
    if (drawer) drawer.classList.add('active');
    if (overlay) overlay.classList.add('active');
    if (hamburger) hamburger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    if (hamburger) hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  if (hamburger) hamburger.addEventListener('click', openDrawer);
  if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
  if (overlay) overlay.addEventListener('click', closeDrawer);

  // Close drawer on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDrawer();
  });

  // Sticky header scroll elevation
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        header.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.45)';
        header.style.background = 'var(--bg-glass-heavy)';
      } else {
        header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        header.style.background = 'var(--bg-glass)';
      }
    }, { passive: true });
  }

  // Account dropdown toggle on touch devices
  const accountBtn = document.getElementById('account-menu-btn');
  const accountMenu = document.getElementById('account-dropdown-menu');
  if (accountBtn && accountMenu) {
    accountBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      accountMenu.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!accountBtn.contains(e.target) && !accountMenu.contains(e.target)) {
        accountMenu.classList.remove('show');
      }
    });
  }
});
