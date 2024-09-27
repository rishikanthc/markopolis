---
title: Rendering Markdown as HTML
date: 09-22-2024
tags:
  - markdown
  - mdsvex
publish: true
---

This document provides an in-depth explanation of the markdown parsing process used in the Marco Polo's application. The parsing is implemented using the `md-swex` library, which allows for the integration of Svelte components within markdown files.
## Parsing Process
1. **Markdown to HTML Conversion**:
   - The `md-swex` library is used to parse markdown files and convert them into HTML blocks.
   - The `compile` function of `md-swex` is utilized to directly compile markdown content.
2. **Database Storage**:
   - Parsed content is stored in the PocketBase database.
   - Fields include ID, title, parsed HTML content, URL, markdown file, front matter (as JSON), and relational fields for backlinks and forward links.
3. **Plugins and Extensions**:
   - **Remark Plugins**: Used for processing markdown abstract syntax trees.
     - `Remark Math`: Renders LaTeX equations.
     - `Remark Footnotes`: Processes footnotes.
     - `Custom Wikilink Plugin`: Resolves relative links.
     - `Custom Obsidian Image Plugin`: Handles inline images.
     - `Custom Remark Mermaid Plugin`: Processes Mermaid diagrams.
4. **Custom Wikilink Plugin**:
   - Recognizes Wikilink syntax and evaluates relative paths.
   - Uses front matter to access the file path and resolve links.
5. **Handling Code Blocks**:
   - Addresses issues with `md-swex` parsing code blocks as inline HTML.
   - Cleanup functions remove unwanted syntax to ensure proper rendering.
6. **Operational Checks**:
   - Ensures the existence of necessary database collections (e.g., `mdbase`, `attachments`).
   - Handles file uploads and updates, storing markdown and image files appropriately.
## Conclusion
The markdown parsing component is integral to the Marco Polo's application, enabling efficient storage and retrieval of markdown content. The use of `md-swex` and various plugins ensures robust parsing and rendering capabilities.
