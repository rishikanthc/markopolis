import os
import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
import regex as mre
import yaml
import re
from .config import settings

MDROOT = settings.md_path


def list_markdown_files():
    if not os.path.exists(MDROOT):
        return None, f"The directory {MDROOT} does not exist."
    files = [
        os.path.splitext(file)[0] for file in os.listdir(MDROOT) if file.endswith(".md")
    ]
    return files, None


def get_meta(note_title):
    if not note_title or not isinstance(note_title, str):
        return None, "Invalid note title"

    note_path = os.path.join(MDROOT, note_title + ".md")
    if not os.path.exists(note_path):
        return None, f"The file {note_path} does not exist."

    try:
        with open(note_path, "r") as file:
            lines = file.readlines()
            if not lines or lines[0].strip() != "---":
                return {}, None  # Return empty dict if no front matter
            yaml_lines = []
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                yaml_lines.append(line)
            metadata = yaml.safe_load("".join(yaml_lines))
            if metadata is None:
                return {}, None
            if not isinstance(metadata, dict):
                return None, "Invalid YAML structure: expected a dictionary"
            return metadata, None
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
            ]
        )

        # Convert Markdown to HTML
        html_content = md.convert(markdown_content)

        return (markdown_content, html_content), None
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

        return toc, None
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
        return backlinks, None
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
