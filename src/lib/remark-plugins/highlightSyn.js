import { visit } from 'unist-util-visit'

function remarkHighlight() {
  return (tree) => {
    visit(tree, 'text', (node, index, parent) => {
      const matches = node.value.match(/==(.*?)==/g)
      if (!matches) return

      const children = []
      let lastIndex = 0

      matches.forEach((match) => {
        const startIndex = node.value.indexOf(match, lastIndex)
        const endIndex = startIndex + match.length

        // Add text before the highlight
        if (startIndex > lastIndex) {
          children.push({
            type: 'text',
            value: node.value.slice(lastIndex, startIndex)
          })
        }

        // Add the highlighted text with a span and class
        children.push({
          type: 'span',
          data: {
          	hName: 'span',
          	hProperties: {
          		className: ['highlight']
          	}
          },
          children: [
            {
              type: 'text',
              value: match.slice(2, -2) // Remove '==' from the start and end
            }
          ]
        })

        lastIndex = endIndex
      })

      // Add any remaining text after the last highlight
      if (lastIndex < node.value.length) {
        children.push({
          type: 'text',
          value: node.value.slice(lastIndex)
        })
      }

      // Replace the original node with the new children
      parent.children.splice(index, 1, ...children)
    })
  }
}

export default remarkHighlight
