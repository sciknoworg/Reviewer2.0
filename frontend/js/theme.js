(function () {
  const STORAGE_KEY = "reviewer2-theme";
  const root = document.documentElement;

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      // localStorage unavailable (private mode, etc.) -- theme just won't persist
    }
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.setAttribute("aria-pressed", String(theme === "dark"));
  }

  // The <head> inline script already set data-theme before first paint;
  // this just keeps the toggle button's aria-pressed state in sync.
  applyTheme(root.getAttribute("data-theme") || "light");

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      setStoredTheme(next);
    });
  });
})();
