document.addEventListener("DOMContentLoaded", function () {
  // Login spinner
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      const spinner = document.getElementById("loginSpinner");
      const btnText = document.getElementById("btnText");
      if (spinner && btnText) {
        spinner.style.display = "inline-block";
        btnText.textContent = "Signing in...";
      }
    });
  }

  // Sidebar toggle on mobile
  const toggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
    document.addEventListener("click", function (e) {
      if (sidebar.classList.contains("show") && !sidebar.contains(e.target) && e.target !== toggle) {
        sidebar.classList.remove("show");
      }
    });
  }
});
