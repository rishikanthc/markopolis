import os
import markdown
from typing import Dict, Optional, Any, Tuple, List
from markdown.extensions.wikilinks import WikiLinkExtension
from datetime import datetime
import platform
import regex as mre
import yaml
import re
from .config import settings
from loguru import logger

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


def get_note_content(note_path: str) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
    if not note_path or not isinstance(note_path, str):
        return None, "Invalid note path"
    full_note_path = os.path.join(MDROOT, note_path + ".md")
    if not os.path.exists(full_note_path):
        return None, f"The file {full_note_path} does not exist."
    try:
        with open(full_note_path, "r") as file:
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
                "markdown_checklist.extension",
                # "mdx_math",
            ]
        )
        # Convert Markdown to HTML
        html_content = md.convert(markdown_content)
        return (markdown_content, html_content), ""
    except Exception as e:
        return None, f"Error reading or processing file: {e}"


def get_toc(note_path: str) -> Tuple[Optional[Dict[str, Dict]], Optional[str]]:
    if not note_path or not isinstance(note_path, str):
        return None, "Invalid note path"
    full_note_path = os.path.join(MDROOT, note_path + ".md")
    if not os.path.exists(full_note_path):
        return None, f"The file {full_note_path} does not exist."
    try:
        with open(full_note_path, "r") as file:
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
        toc: Dict[str, Dict] = {}
        current_levels: Dict[int, Dict] = {0: toc}
        for level, title in headings:
            new_dict: Dict[str, Dict] = {}
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


def get_backlinks_slow(note_path: str) -> Tuple[Optional[List[str]], Optional[str]]:
    if not note_path or not isinstance(note_path, str):
        return None, "Invalid note path"
    try:
        backlinks = []
        note_name = os.path.basename(note_path)
        note_name_without_ext = os.path.splitext(note_name)[0]

        # Create different patterns to match various link formats
        patterns = [
            rf"\[\[\s*{re.escape(note_path)}\s*(\|[^\]]+)?\s*\]\]",  # Full path
            rf"\[\[\s*{re.escape(note_name_without_ext)}\s*(\|[^\]]+)?\s*\]\]",  # Just the filename without extension
            rf"\[.*\]\(.*{re.escape(note_path)}.*\)",  # Markdown link with full path
            rf"\[.*\]\(.*{re.escape(note_name)}.*\)",  # Markdown link with filename
        ]

        for root, _, files in os.walk(MDROOT):
            for filename in files:
                if filename.endswith(".md"):
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, MDROOT)
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                backlinks.append(relative_path)
                                logger.info(
                                    f"Backlink found in {relative_path} for {note_path}"
                                )
                                break  # No need to check other patterns for this file

        logger.info(f"Found {len(backlinks)} backlinks for {note_path}")
        return backlinks, ""
    except Exception as e:
        logger.error(f"Error processing backlinks for {note_path}: {e}")
        return None, f"Error processing backlinks: {e}"


def fuzzy_search_in_text(search_term, max_dist=2):
    """
    Perform a fuzzy search on the contents of files and return matches ordered by closeness.
    """
    logger.info(
        f"Starting fuzzy search for term: {search_term} with max_dist: {max_dist}"
    )
    logger.info(f"MDROOT: {MDROOT}")

    matches_with_distances = []
    pattern = f"({search_term}){{e<={max_dist}}}"

    try:
        for root, _, files in os.walk(MDROOT):
            for file_name in files:
                if not file_name.endswith(".md"):
                    continue
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, MDROOT)

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        match = mre.search(pattern, content, mre.BESTMATCH)
                        if match:
                            distance = match.fuzzy_counts[0]
                            snippet_start = max(match.start() - 30, 0)
                            snippet_end = min(match.end() + 30, len(content))
                            snippet = content[snippet_start:snippet_end]
                            matches_with_distances.append(
                                (
                                    relative_path,
                                    snippet,
                                    distance,
                                )
                            )
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {str(e)}")

        sorted_matches = sorted(matches_with_distances, key=lambda x: x[2])
        logger.info(f"Total matches found: {len(sorted_matches)}")
        return [(match[0], match[1]) for match in sorted_matches]
    except Exception as e:
        logger.exception(f"Unexpected error in fuzzy search: {str(e)}")
        return []


def raw(note_path: str) -> Tuple[Optional[str], Optional[str]]:
    # Remove any file extension if present
    note_path = os.path.splitext(note_path)[0]
    file_path = os.path.join(MDROOT, f"{note_path}.md")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content, None
    except FileNotFoundError:
        error_msg = f"Error: File '{file_path}' not found."
        logger.error(error_msg)
        return None, error_msg
    except IOError as e:
        error_msg = f"Error: Unable to read the file '{file_path}'. {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error reading '{file_path}': {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def create_markdown_files(markdown_dict):
    try:
        files_created = 0
        for path, content in markdown_dict.items():
            # Normalize the path to handle different separators
            normalized_path = os.path.normpath(path)

            # Construct the full file path
            file_path = os.path.join(MDROOT, normalized_path)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Add .md extension if not present
            if not file_path.endswith(".md"):
                file_path += ".md"

            # Write the content to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            files_created += 1
            logger.info(f"Created file: {file_path}")

        logger.info(
            f"Created {files_created} markdown files in the '{MDROOT}' directory."
        )
        return 200  # Success
    except Exception as e:
        logger.error(f"An error occurred while creating markdown files: {str(e)}")
        return 500  # Internal Server Error
