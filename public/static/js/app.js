/**
 * app/static/js/app.js
 * Minimal vanilla JavaScript for the mobile shop.
 * Keep this small — HTMX handles most interactions.
 */

// ── Mobile Navigation Toggle ──────────────────────────────────────────────
function toggleMobileMenu() {
  const menu = document.getElementById("mobile-menu");
  if (menu) {
    menu.classList.toggle("hidden");
  }
}

// Close mobile menu when a link is clicked
document.addEventListener("DOMContentLoaded", function () {
  const mobileLinks = document.querySelectorAll("#mobile-menu a");
  mobileLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      const menu = document.getElementById("mobile-menu");
      if (menu) menu.classList.add("hidden");
    });
  });

  // ── Sticky navbar shadow on scroll ────────────────────────────────────
  const navbar = document.querySelector("nav");
  if (navbar) {
    window.addEventListener("scroll", function () {
      if (window.scrollY > 10) {
        navbar.classList.add("shadow-md");
      } else {
        navbar.classList.remove("shadow-md");
      }
    });
  }

  // ── Admin: Auto-dismiss flash messages ───────────────────────────────
  const flashMsg = document.querySelector(".flash-message");
  if (flashMsg) {
    setTimeout(function () {
      flashMsg.style.opacity = "0";
      flashMsg.style.transition = "opacity 0.5s";
      setTimeout(function () { flashMsg.remove(); }, 500);
    }, 3000);
  }

  // ── HTMX: Scroll to top of product grid after search ────────────────
  document.addEventListener("htmx:afterSettle", function (evt) {
    if (evt.detail.target && evt.detail.target.id === "product-grid") {
      const grid = document.getElementById("product-grid");
      if (grid) {
        grid.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
  });
});
