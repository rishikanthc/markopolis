import { visit } from 'unist-util-visit';

function remarkTags() {
	return (tree) => {
		visit(tree, 'text', (node, index, parent) => {
			const matches = node.value.match(/#[a-zA-Z0-9_-]+/g);
			if (!matches) return;

			const children = [];
			let lastIndex = 0;

			matches.forEach((match) => {
				const startIndex = node.value.indexOf(match, lastIndex);
				const endIndex = startIndex + match.length;

				// Add text before the tag
				if (startIndex > lastIndex) {
					children.push({
						type: 'text',
						value: node.value.slice(lastIndex, startIndex)
					});
				}

				// Add the tag with a span and class, including an anchor tag
				const tagName = match.slice(1); // Remove '#' from the start
				children.push({
					type: 'span',
					data: {
						hName: 'span',
						hProperties: {
							className: ['tag']
						}
					},
					children: [
						{
							type: 'element',
							data: {
								hName: 'a',
								hProperties: {
									href: `/tags/${tagName}`,
									className: ['tag-link']
								}
							},
							children: [
								{
									type: 'text',
									value: tagName
								}
							]
						}
					]
				});

				lastIndex = endIndex;
			});

			// Add any remaining text after the last tag
			if (lastIndex < node.value.length) {
				children.push({
					type: 'text',
					value: node.value.slice(lastIndex)
				});
			}

			// Replace the original node with the new children
			parent.children.splice(index, 1, ...children);
		});
	};
}

export default remarkTags;
