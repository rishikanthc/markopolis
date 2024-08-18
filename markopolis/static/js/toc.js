document.addEventListener("DOMContentLoaded", function () {
  const tocItems = document.querySelectorAll(".toc-item a");
  const sections = Array.from(tocItems).map((item) => {
    const targetId = item.getAttribute("href").substring(1);
    return document.getElementById(targetId);
  });

  const sensitivityOffset = 200; // Adjust this value if needed

  function updateActiveTOC() {
    let currentActiveIndex = -1;

    sections.forEach((section, index) => {
      if (section) {
        const rect = section.getBoundingClientRect();
        const nextSection = sections[index + 1];
        const nextRect = nextSection
          ? nextSection.getBoundingClientRect()
          : null;

        // Check if the current section is within the viewport and above sensitivityOffset
        if (
          rect.top <= sensitivityOffset &&
          (!nextRect || nextRect.top > sensitivityOffset)
        ) {
          currentActiveIndex = index;
        }
      }
    });

    // Update the active class for TOC items
    tocItems.forEach((item, index) => {
      if (index === currentActiveIndex) {
        item.parentElement.classList.add("active");
      } else {
        item.parentElement.classList.remove("active");
      }
    });
  }

  // Ensure the scroll event listener is attached to the right element
  const contentElement = document.querySelector(".main");

  if (contentElement) {
    contentElement.addEventListener("scroll", updateActiveTOC);
    updateActiveTOC(); // Trigger once on page load
  }
});
