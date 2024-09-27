// src/lib/md.ts

import yaml from 'js-yaml';

/**
 * Function to add or update frontmatter in Markdown content.
 *
 * @param fileContent - The content of the Markdown file as a string.
 * @param url - The URL to be added to the frontmatter.
 * @returns The modified Markdown content with updated frontmatter.
 */
export function addFrontmatterToMarkdown(fileContent: string, url: string): string {
  // Regular expression to detect existing YAML frontmatter
  const frontmatterRegex = /^---\n([\s\S]*?)\n---\n/;
  const match = fileContent.match(frontmatterRegex);

  let newContent: string;

  if (match) {
    // YAML frontmatter exists, parse the existing frontmatter
    const existingFrontmatter = yaml.load(match[1]) as Record<string, any> || {};

    // Add or update the 'url' field in the frontmatter
    existingFrontmatter['mdpath'] = url;

    // Convert the updated frontmatter back to YAML format
    const updatedFrontmatter = yaml.dump(existingFrontmatter);

    // Replace the old frontmatter with the updated one
    newContent = fileContent.replace(frontmatterRegex, `---\n${updatedFrontmatter}---\n`);
  } else {
    // No frontmatter exists, create new frontmatter
    const newFrontmatter = yaml.dump({ url });

    // Prepend the new frontmatter to the file content
    newContent = `---\n${newFrontmatter}---\n${fileContent}`;
  }

  // Return the updated content
  return newContent;
}
