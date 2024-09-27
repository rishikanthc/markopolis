import { visit } from 'unist-util-visit';

function obsidianImagePlugin() {
  return (tree) => {
    visit(tree, 'paragraph', (node) => {
      const newChildren = [];
      let i = 0;

      while (i < node.children.length) {
        const currentNode = node.children[i];

        // Check if the current node is a 'text' node with a '!'
        if (currentNode.type === 'text' && currentNode.value === '!') {
          // Check if the next node is a 'wikiLink' node with an image file extension
          const nextNode = node.children[i + 1];
          if (
            nextNode &&
            nextNode.type === 'wikiLink' &&
            /\.(png|jpe?g|gif|svg|webp)$/.test(nextNode.value)
          ) {
            // Replace the '!' and 'wikiLink' with an 'image' node
            let newUrl = '/api/img/' + nextNode.value;
            newChildren.push({
              type: 'image',
              url: newUrl,
              alt: nextNode.value.split('/').pop() // Use the filename as the alt text
            });
            i += 2; // Skip both the 'text' and 'wikiLink' nodes
            continue;
          }
        }

        // If no match, just push the current node as-is
        newChildren.push(currentNode);
        i++;
      }

      // Replace the old children with the new set of children
      node.children = newChildren;
    });
  };
}

export default obsidianImagePlugin;
