import { visit } from 'unist-util-visit';

// Create the plugin
const remarkMermaid = () => {
  return (tree) => {
    visit(tree, 'code', (node) => {
      if (node.lang === 'mermaid') {
        // Replace the code block with a custom HTML structure
        node.type = 'html';
        node.value = `<div class="mermaid">${node.value}</div>`;
      }
    });
  };
};

export default remarkMermaid;
