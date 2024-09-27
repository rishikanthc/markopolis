// src/lib/plugins/remark-footnote-html.js
import { visit } from 'unist-util-visit';


function remarkFootnoteHTML() {
  return (tree) => {
    const footnotes = [];
    const footnoteMap = {};

    // Collect footnote definitions
    visit(tree, 'footnoteDefinition', (node) => {
      const identifier = node.identifier;
      const content = node.children;
      footnoteMap[identifier] = content;
      console.log(node)
    });

    // Replace footnote references with custom HTML
    visit(tree, 'footnoteReference', (node, index, parent) => {
      const identifier = node.identifier;
      const footnoteNumber = Object.keys(footnoteMap).indexOf(identifier) + 1;

      if (footnoteNumber === 0) return;

      const sup = {
        type: 'html',
        value: `<sup id="fnref${footnoteNumber}"><a href="#fn${footnoteNumber}" aria-describedby="footnote">${footnoteNumber}</a></sup>`,
      };

      parent.children.splice(index, 1, sup);
    });

    // Remove footnote definitions from the tree
    tree.children = tree.children.filter((node) => node.type !== 'footnoteDefinition');

    // Append the footnotes section at the end
    const footnotesSection = {
      type: 'html',
      value: '<section class="footnotes"><ol>',
    };

    tree.children.push(footnotesSection);

    Object.keys(footnoteMap).forEach((identifier, idx) => {
      const footnoteNumber = idx + 1;
      const content = footnoteMap[identifier]
        .map((child) => {
          if (child.type === 'text') {
            return child.value;
          } else {
            // Handle other node types as needed
            return '';
          }
        })
        .join('');

      const footnoteItem = {
        type: 'html',
        value: `<li id="fn${footnoteNumber}">${content} <a href="#fnref${footnoteNumber}" aria-label="Back to content">↩︎</a></li>`,
      };

      tree.children.push(footnoteItem);
    });

    // Close the ordered list and section
    tree.children.push({
      type: 'html',
      value: '</ol></section>',
    });
  };
}

export default remarkFootnoteHTML;
