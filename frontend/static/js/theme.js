/**
 * SoundSphere Dark / Light Theme Manager
 * Persists theme choice in localStorage and synchronizes toggle icon & SVGs.
 */

(function() {
  const THEME_KEY = 'soundsphere_theme';

  function getPreferredTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    updateThemeToggleIcons(theme);
  }

  function updateThemeToggleIcons(theme) {
    const moonIcons = document.querySelectorAll('.icon-moon');
    const sunIcons = document.querySelectorAll('.icon-sun');

    if (theme === 'light') {
      moonIcons.forEach(el => el.style.display = 'block');
      sunIcons.forEach(el => el.style.display = 'none');
    } else {
      moonIcons.forEach(el => el.style.display = 'none');
      sunIcons.forEach(el => el.style.display = 'block');
    }

    // Also update any text/emoji toggle buttons
    document.querySelectorAll('.theme-toggle-btn:not(#theme-toggle)').forEach(btn => {
      btn.innerHTML = theme === 'light' 
        ? '<span title="Switch to Dark Mode">🌙</span>' 
        : '<span title="Switch to Light Mode">☀️</span>';
    });
  }

  // Apply immediately on script execution to prevent flash
  const initialTheme = getPreferredTheme();
  applyTheme(initialTheme);

  document.addEventListener('DOMContentLoaded', () => {
    updateThemeToggleIcons(document.documentElement.getAttribute('data-theme') || initialTheme);
  });

  // Delegation keeps the toggle working even if the header is replaced or loaded later.
  document.addEventListener('click', (e) => {
    const button = e.target.closest('#theme-toggle, .theme-toggle-btn');
    if (!button) return;

    e.preventDefault();
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    if (window.SoundSphere && typeof window.SoundSphere.toast === 'function') {
      SoundSphere.toast(`Switched to ${next === 'dark' ? 'Stealth Dark' : 'Clean Light'} Mode`, 'info', 1800);
    }
  });
})();
