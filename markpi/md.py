import os
import markdown
import yaml
from yaml.constructor import ConstructorError
import re
from collections import defaultdict

# Global variable for the directory containing markdown files
MDROOT = "../md-test"

__all__ = [
    "list_markdown_files",
    "get_meta",
    "get_note_as_html",
    "get_backlinks_slow",
    "sanitize_title",
]


def list_markdown_files():
    """
    List all markdown files in the directory specified by MDROOT.
    Returns:
        List of markdown file names without extensions.
    """
    # Ensure MDROOT is defined
    if not os.path.exists(MDROOT):
        raise ValueError(f"The directory {MDROOT} does not exist.")

    # List to store markdown file names without extensions
    markdown_files = []

    # Iterate over all files in the directory
    for file in os.listdir(MDROOT):
        # Check if the file has a .md extension
        if file.endswith(".md"):
            # Add the file name without extension to the list
            markdown_files.append(os.path.splitext(file)[0])

    return markdown_files


def get_meta(note_title):
    """
    Get meta data of note specified by note title.
    Looks for note in `MDROOT`.
    Args:
        note_title (str): The title of the note (without .md extension).
    Returns:
        dict: A dictionary containing the YAML front matter metadata.
    """
    # Construct the full path to the markdown file
    note_path = os.path.join(MDROOT, note_title + ".md")

    if not os.path.exists(note_path):
        raise FileNotFoundError(f"The file {note_path} does not exist.")

    with open(note_path, "r") as file:
        # Read the file contents
        lines = file.readlines()

        # Check if the file starts with '---' indicating the start of YAML front matter
        if lines[0].strip() != "---":
            raise ValueError("The file does not contain valid YAML front matter.")

        # Extract the YAML front matter
        yaml_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            yaml_lines.append(line)

        # Parse the YAML front matter with a custom loader to treat dates as strings
        try:
            metadata = yaml.safe_load("".join(yaml_lines))
        except ConstructorError as e:
            raise ValueError(f"Error parsing YAML front matter: {e}")

        return metadata


def get_note_as_html(note_title):
    """
    Returns the content of the note specified by its title as HTML.
    Content excludes front-matter if present.

    Args:
        note_title (str): The title of the note (without .md extension).

    Returns:
        str: HTML formatted note content.
    """
    # Construct the full path to the markdown file
    note_path = os.path.join(MDROOT, note_title + ".md")

    if not os.path.exists(note_path):
        raise FileNotFoundError(f"The file {note_path} does not exist.")

    with open(note_path, "r") as file:
        # Read the file contents
        lines = file.readlines()

        # Skip YAML front matter if present
        content_lines = []
        in_front_matter = False
        for line in lines:
            if line.strip() == "---":
                in_front_matter = not in_front_matter
                continue

            if not in_front_matter:
                content_lines.append(line)

        # Join the content lines
        content = "".join(content_lines)

        # Convert Markdown content to HTML
        html_content = markdown.markdown(content)

        return html_content


def get_toc(note_title):
    """
    Generates Table of Contents for a note specified by its title.
    ToC will include headings and sub-headings of all h# levels.

    Args:
        note_title (str): The title of the note (without .md extension).

    Returns:
        dict: Nested dictionary of headings and sub-headings.
    """
    # Construct the full path to the markdown file
    note_path = os.path.join(MDROOT, note_title + ".md")

    if not os.path.exists(note_path):
        raise FileNotFoundError(f"The file {note_path} does not exist.")

    with open(note_path, "r") as file:
        # Read the file contents
        lines = file.readlines()

        # Skip YAML front matter if present
        content_lines = []
        in_front_matter = False
        for line in lines:
            if line.strip() == "---":
                in_front_matter = not in_front_matter
                continue

            if not in_front_matter:
                content_lines.append(line)

        # Extract headings from the content lines
        headings = []
        heading_pattern = re.compile(r"^(#{1,6})\s+(.*)")

        for line in content_lines:
            match = heading_pattern.match(line)
            if match:
                level = len(
                    match.group(1)
                )  # Number of '#' characters indicates the heading level
                title = match.group(2).strip()
                if title:  # Ensure the heading is not empty
                    headings.append((level, title))

        # Create a nested dictionary for the ToC
        toc = defaultdict(dict)

        def add_to_toc(toc, level, title):
            if level == 1:
                toc[title] = {}
            else:
                for key in toc:
                    add_to_toc(toc[key], level - 1, title)

        for level, title in headings:
            add_to_toc(toc, level, title)

        return dict(toc)


def sanitize_title(note_title):
    """
    Sanitize the note title for use in regular expressions.

    Args:
        note_title (str): The original note title.

    Returns:
        str: The sanitized note title ready for use in a regular expression.
    """
    # Remove leading/trailing whitespace and escape special regex characters
    return re.escape(note_title.strip())


def get_backlinks_slow(note_title):
    """
    Get the list of all notes which link to this note_title, using
    wikilink syntax.
    Note:
        when mapping from wikilinks to the corresponding note file, remember
        that file names will replace any spaces or incompatible file naming conventions with
        a hyphen instead. Account for this
    Returns:
        list of note titles (file-names with .md extension)
    """
    backlinks = []
    sanitized_title = sanitize_title(note_title)
    # Replace escaped spaces with a pattern matching any whitespace
    sanitized_title = sanitized_title.replace("\\ ", r"\s+")
    for filename in os.listdir(MDROOT):
        filename = filename.strip()  # Remove any leading/trailing whitespace
        if filename.endswith(".md"):
            with open(os.path.join(MDROOT, filename), "r") as file:
                content = file.read()
                # Look for wikilinks matching the sanitized note title, allowing for flexible whitespace
                if re.search(
                    r"\[\[\s*" + sanitized_title + r"\s*(\|[^\]]+)?\s*\]\]",
                    content,
                    re.IGNORECASE,
                ):
                    backlinks.append(filename)
    return backlinks
