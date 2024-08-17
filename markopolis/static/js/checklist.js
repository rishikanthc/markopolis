// checklist.js - Interactive Markdown checklists

class Checklists {
  constructor(container) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.checkboxSelector = "ul > li > input[type='checkbox']";

    if (!this.container) {
      console.error('Checklists: Container not found:', container);
      return;
    }

    this.initializeCheckboxes();
  }

  initializeCheckboxes() {
    const checkboxes = this.container.querySelectorAll(this.checkboxSelector);
    console.log(`Found ${checkboxes.length} checkboxes`);

    checkboxes.forEach((checkbox, index) => {
      checkbox.disabled = false;
      checkbox.addEventListener('change', (event) => this.onChange(event, index));
      console.log(`Initialized checkbox ${index}: ${checkbox.checked ? 'checked' : 'unchecked'}`);
    });
  }

  onChange(event, index) {
    const checkbox = event.target;
    console.log(`Checkbox ${index} changed. New state: ${checkbox.checked}`);

    // Update the checkbox state in the DOM
    checkbox.checked = checkbox.checked;

    // If you need to update any other part of the page or send data to a server, do it here
    // For example:
    // this.updateServer(index, checkbox.checked);

    console.log(`Checkbox ${index} update complete`);
  }

  // Example method to update server (implement if needed)
  // updateServer(index, isChecked) {
  //   console.log(`Sending update to server: Checkbox ${index} is now ${isChecked ? 'checked' : 'unchecked'}`);
  //   // Implement server update logic here
  // }
}

// Initialize Checklists when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM fully loaded and parsed');
  try {
    const contentElement = document.querySelector('.content, article, .article');
    if (!contentElement) {
      console.error('Checklists: Content element not found');
      return;
    }

    new Checklists(contentElement);
    console.log('Checklists initialized');
  } catch (error) {
    console.error('Error initializing Checklists:', error);
  }
});
