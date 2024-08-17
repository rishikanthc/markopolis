const themeSwitcher = document.getElementById("theme-switcher");
const themeText = document.getElementById("theme-text");
const currentTheme = localStorage.getItem("theme") || "light";

document.documentElement.setAttribute("data-theme", currentTheme);
updateThemeToggle(currentTheme);
updateHighlightTheme(currentTheme);

themeSwitcher.addEventListener("click", toggleTheme);
themeSwitcher.addEventListener("touchend", function (e) {
  e.preventDefault();
  toggleTheme();
});
themeSwitcher.addEventListener("keydown", function (e) {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    toggleTheme();
  }
});

function toggleTheme() {
  let theme = document.documentElement.getAttribute("data-theme");
  theme = theme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  updateThemeToggle(theme);
  updateHighlightTheme(theme);
}

function updateThemeToggle(theme) {
  if (theme === "dark") {
    themeSwitcher.classList.add("dark");
    themeSwitcher.setAttribute("aria-label", "Switch to light mode");
    themeText.textContent = "Light mode";
  } else {
    themeSwitcher.classList.remove("dark");
    themeSwitcher.setAttribute("aria-label", "Switch to dark mode");
    themeText.textContent = "Dark mode";
  }
}

function updateHighlightTheme(theme) {
  document.getElementById("light-theme").disabled = theme === "dark";
  document.getElementById("dark-theme").disabled = theme === "light";
}
