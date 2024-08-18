document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("search-input");
  const searchResults = document.getElementById("search-results");
  const commandPalette = document.querySelector(".command-palette");
  let activeIndex = -1;

  document.addEventListener("keydown", function (event) {
    if (event.ctrlKey && event.key === "k") {
      event.preventDefault();
      toggleCommandPalette();
    }
  });

  document.addEventListener("click", function (event) {
    if (
      !commandPalette.contains(event.target) &&
      !event.target.matches("#search-toggle")
    ) {
      commandPalette.style.display = "none";
    }
  });

  document.addEventListener("touchend", function (event) {
    if (
      !commandPalette.contains(event.target) &&
      !event.target.matches("#search-toggle")
    ) {
      commandPalette.style.display = "none";
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      commandPalette.style.display = "none";
    }
  });

  if (searchInput) {
    searchInput.addEventListener("input", async function () {
      const query = searchInput.value.trim();
      if (query.length > 0) {
        const response = await fetch(`/api/search/${query}`);
        const results = await response.json();
        searchResults.innerHTML = results.results
          .map((result) => {
            const filePath = result.file_path;
            const fileNameWithoutExtension = filePath.replace(/\.md$/, "");
            return `
          <div class="search-result">
            <a href="/${fileNameWithoutExtension}">
              <strong>${fileNameWithoutExtension}</strong>: ${result.snippet}
            </a>
          </div>
        `;
          })
          .join("");
        searchResults.style.display = "block";
        activeIndex = -1;
      } else {
        searchResults.innerHTML = "";
        searchResults.style.display = "none";
      }
    });

    document.addEventListener("keydown", function (event) {
      const results = document.querySelectorAll(".search-result");
      if (commandPalette.style.display === "block" && results.length > 0) {
        if (event.key === "ArrowDown") {
          event.preventDefault();
          activeIndex = (activeIndex + 1) % results.length;
          updateActiveResult(results);
        } else if (event.key === "ArrowUp") {
          event.preventDefault();
          activeIndex = (activeIndex - 1 + results.length) % results.length;
          updateActiveResult(results);
        } else if (event.key === "Enter" && activeIndex >= 0) {
          results[activeIndex].querySelector("a").click();
        }
      }
    });

    function updateActiveResult(results) {
      results.forEach((result, index) => {
        if (index === activeIndex) {
          result.classList.add("active-result");
          result.scrollIntoView({ block: "nearest" });
        } else {
          result.classList.remove("active-result");
        }
      });
    }

    searchInput.addEventListener("click", function (event) {
      event.stopPropagation();
    });
  }

  // Mobile menu toggle
  const menuToggle = document.getElementById("menu-toggle");
  const sidebar = document.querySelector(".left");

  function toggleSidebar(event) {
    event.preventDefault();
    sidebar.classList.toggle("active");
  }

  menuToggle.addEventListener("click", toggleSidebar);
  menuToggle.addEventListener("touchend", toggleSidebar);

  // Mobile search toggle
  const searchToggle = document.getElementById("search-toggle");

  function handleSearchToggle(event) {
    event.preventDefault();
    event.stopPropagation();
    toggleCommandPalette();
  }

  searchToggle.addEventListener("click", handleSearchToggle);
  searchToggle.addEventListener("touchend", handleSearchToggle);

  function toggleCommandPalette() {
    if (commandPalette.style.display === "block") {
      commandPalette.style.display = "none";
    } else {
      commandPalette.style.display = "block";
      searchInput.focus();
    }
  }
});
