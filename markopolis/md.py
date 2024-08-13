import os
import markdown
from typing import Dict, Optional, Any, Tuple
from markdown.extensions.wikilinks import WikiLinkExtension
from datetime import datetime
import platform
import regex as mre
import yaml
import re
from .config import settings

MDROOT = settings.md_path


def list_markdown_files():
    if not os.path.exists(MDROOT):
        return None, f"The directory {MDROOT} does not exist."

    files = []
    for root, _, filenames in os.walk(MDROOT):
        for filename in filenames:
            if filename.endswith(".md"):
                # Get the relative path from MDROOT
                rel_path = os.path.relpath(os.path.join(root, filename), MDROOT)
                # Remove the .md extension
                rel_path_without_ext = os.path.splitext(rel_path)[0]
                files.append(rel_path_without_ext)

    return files, ""


def clean_filename(filename):
    """Clean the filename to be used as a title."""
    # Remove the .md extension
    name = os.path.splitext(filename)[0]
    # Replace hyphens with spaces and capitalize words
    return " ".join(word.capitalize() for word in name.replace("-", " ").split())


def get_meta(note_path: str) -> Tuple[Optional[Dict[str, Any]], str]:
    if not note_path or not isinstance(note_path, str):
        return None, "Invalid note path"

    full_note_path = os.path.join(MDROOT, note_path + ".md")
    if not os.path.exists(full_note_path):
        return None, f"The file {full_note_path} does not exist."

    try:
        with open(full_note_path, "r") as file:
            content = file.read()
            if content.strip().startswith("---"):
                # Split the content at the second occurrence of "---"
                _, front_matter, _ = content.split("---", 2)
                metadata = yaml.safe_load(front_matter)
                if metadata is None:
                    metadata = {}
                if not isinstance(metadata, dict):
                    return None, "Invalid YAML structure: expected a dictionary"
            else:
                metadata = {}  # No front matter, use empty dict

        # Add default values for missing fields
        if "title" not in metadata or not metadata["title"]:
            metadata["title"] = clean_filename(os.path.basename(full_note_path))
        if "tags" not in metadata:
            metadata["tags"] = []
        elif not isinstance(metadata["tags"], list):
            metadata["tags"] = [metadata["tags"]]  # Convert to list if it's not already
        if "date" not in metadata:
            # Get file creation date
            if platform.system() == "Windows":
                creation_time = os.path.getctime(full_note_path)
            else:  # Unix-based systems
                stat = os.stat(full_note_path)
                try:
                    creation_time = stat.st_birthtime  # macOS
                except AttributeError:
                    creation_time = stat.st_mtime  # Linux and other Unix
            metadata["date"] = datetime.fromtimestamp(creation_time)

        # Add the relative path to the metadata
        metadata["path"] = note_path

        # Move any unrecognized fields to custom_fields
        recognized_fields = {"title", "date", "tags", "path"}
        custom_fields = {
            k: v for k, v in metadata.items() if k not in recognized_fields
        }

        # Convert boolean values in custom_fields to strings
        for key, value in custom_fields.items():
            if isinstance(value, bool):
                custom_fields[key] = str(value).lower()

        # Remove custom fields from the main metadata dict and add them to custom_fields
        for key in custom_fields:
            metadata.pop(key, None)

        metadata["custom_fields"] = custom_fields

        return metadata, ""
    except yaml.YAMLError as e:
        return None, f"Error parsing YAML front matter: {e}"
    except Exception as e:
        return None, f"Error reading file: {e}"


def get_note_content(note_title):
    if not note_title or not isinstance(note_title, str):
        return None, "Invalid note title"
    note_path = os.path.join(MDROOT, note_title + ".md")
    if not os.path.exists(note_path):
        return None, f"The file {note_path} does not exist."
    try:
        with open(note_path, "r") as file:
            content = file.read()

        # Split front matter and content
        parts = content.split("---", 2)
        if len(parts) >= 3:
            markdown_content = parts[2].strip()
        else:
            markdown_content = content

        # Configure Markdown parser with extensions
        md = markdown.Markdown(
            extensions=[
                "fenced_code",
                "codehilite",
                WikiLinkExtension(base_url="/", end_url=""),
                # "mdx_math",
            ]
        )

        # Convert Markdown to HTML
        html_content = md.convert(markdown_content)

        return (markdown_content, html_content), ""
    except Exception as e:
        return None, f"Error reading or processing file: {e}"


def get_toc(note_title: str) -> tuple[None | dict[str, dict], None | str]:
    if not note_title or not isinstance(note_title, str):
        return None, "Invalid note title"
    note_path = os.path.join(MDROOT, note_title + ".md")
    if not os.path.exists(note_path):
        return None, f"The file {note_path} does not exist."
    try:
        with open(note_path, "r") as file:
            content = file.read()

        # Remove front matter
        content_parts = content.split("---", 2)
        if len(content_parts) >= 3:
            content = content_parts[2]

        # Extract headings
        heading_pattern = re.compile(r"^(#{1,6})\s+(.*?)$", re.MULTILINE)
        headings = [
            (len(match.group(1)), match.group(2).strip())
            for match in heading_pattern.finditer(content)
        ]

        # Build TOC
        toc: dict[str, dict] = {}
        current_levels: dict[int, dict] = {0: toc}

        for level, title in headings:
            new_dict: dict[str, dict] = {}
            parent_level = max(k for k in current_levels.keys() if k < level)
            current_levels[parent_level][title] = new_dict
            current_levels[level] = new_dict

            # Clear any deeper levels
            for lvl in list(current_levels.keys()):
                if lvl > level:
                    del current_levels[lvl]

        return toc, ""
    except Exception as e:
        return None, f"Error processing file: {e}"


def get_backlinks_slow(note_title):
    if not note_title or not isinstance(note_title, str):
        return None, "Invalid note title"

    try:
        backlinks = []
        sanitized_title = re.escape(note_title.strip()).replace("\\ ", r"\s+")
        for filename in os.listdir(MDROOT):
            filename = filename.strip()
            if filename.endswith(".md"):
                with open(os.path.join(MDROOT, filename), "r") as file:
                    content = file.read()
                    if re.search(
                        r"\[\[\s*" + sanitized_title + r"\s*(\|[^\]]+)?\s*\]\]",
                        content,
                        re.IGNORECASE,
                    ):
                        backlinks.append(filename)
        return backlinks, ""
    except Exception as e:
        return None, f"Error processing backlinks: {e}"


def fuzzy_search(search_term, max_dist=2):
    """
    Perform a fuzzy search on a list of file names and return matches ordered by closeness.
    :param search_term: The search term to find in the file names.
    :param max_dist: The maximum Levenshtein distance for the fuzzy search.
    :return: List of file names that match the search term, ordered by closeness.
    """
    file_names = os.listdir(MDROOT)
    pattern = f"({search_term}){{e<={max_dist}}}"

    # Find matches and their edit distances
    matches_with_distances = []
    for file_name in file_names:
        match = mre.search(pattern, file_name, mre.BESTMATCH)
        if match:
            # Extract the edit distance from the match object
            distance = match.fuzzy_counts[0]
            matches_with_distances.append((file_name, distance))

    # Sort matches by edit distance (lower distance means closer match)
    sorted_matches = sorted(matches_with_distances, key=lambda x: x[1])

    # Return only the file names, now sorted by closeness
    return [match[0].split(".")[0] for match in sorted_matches]


def fuzzy_search_in_text(search_term, max_dist=2):
    """
    Perform a fuzzy search on the contents of files and return matches ordered by closeness.
    :param search_term: The search term to find in the file contents.
    :param max_dist: The maximum Levenshtein distance for the fuzzy search.
    :return: List of tuples (file name, snippet) that match the search term, ordered by closeness.
    """
    file_names = os.listdir(MDROOT)
    pattern = f"({search_term}){{e<={max_dist}}}"

    matches_with_distances = []

    for file_name in file_names:
        file_path = os.path.join(MDROOT, file_name)
        if not os.path.isfile(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            match = mre.search(pattern, content, mre.BESTMATCH)
            if match:
                # Extract the edit distance from the match object
                distance = match.fuzzy_counts[0]
                snippet_start = max(match.start() - 30, 0)
                snippet_end = min(match.end() + 30, len(content))
                snippet = content[snippet_start:snippet_end]

                matches_with_distances.append((file_name, snippet, distance))

    # Sort matches by edit distance (lower distance means closer match)
    sorted_matches = sorted(matches_with_distances, key=lambda x: x[2])

    # Return only the file names and snippets, now sorted by closeness
    return [(match[0], match[1]) for match in sorted_matches]


def raw(note_title):
    file_path = os.path.join(MDROOT, f"{note_title}.md")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content, ""
    except FileNotFoundError:
        return (
            None,
            f"Error: File '{note_title}.md' not found in the specified directory.",
        )
    except IOError:
        return None, f"Error: Unable to read the file '{note_title}.md'."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def create_markdown_files(markdown_dict):
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(MDROOT, exist_ok=True)

        for title, content in markdown_dict.items():
            # Create a valid filename from the title
            filename = f"{title.replace(' ', '_').lower()}.md"
            file_path = os.path.join(MDROOT, filename)

            # Write the content to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        print(
            f"Created {len(markdown_dict)} markdown files in the '{MDROOT}' directory."
        )
        return 200  # Success
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 500  # Internal Server Error
