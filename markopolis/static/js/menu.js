document.addEventListener("DOMContentLoaded", function () {
  const menuToggle = document.getElementById("menu-toggle");
  const sidebar = document.querySelector(".sidebar");

  // Toggle sidebar on click or touchstart
  function toggleSidebar() {
    sidebar.classList.toggle("active");
  }

  menuToggle.addEventListener("click", toggleSidebar);
  menuToggle.addEventListener("touchstart", toggleSidebar);

  // Close sidebar when clicking or tapping outside of it
  function closeSidebar(event) {
    if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
      sidebar.classList.remove("active");
    }
  }

  document.addEventListener("click", closeSidebar);
  document.addEventListener("touchstart", closeSidebar);
});
