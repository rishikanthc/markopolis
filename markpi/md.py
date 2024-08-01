import os
import markdown
import yaml
import re
from collections import defaultdict

MDROOT = "/Users/rishi/Code/cookiejar/markpi/md-test"


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
            lines = file.readlines()
            content_lines = []
            in_front_matter = False
            for line in lines:
                if line.strip() == "---":
                    in_front_matter = not in_front_matter
                    continue
                if not in_front_matter:
                    content_lines.append(line)
            markdown_content = "".join(content_lines)
            html_content = markdown.markdown(markdown_content)
            return (markdown_content, html_content), None
    except Exception as e:
        return None, f"Error reading or processing file: {e}"


def get_toc(note_title):
    if not note_title or not isinstance(note_title, str):
        return None, "Invalid note title"

    note_path = os.path.join(MDROOT, note_title + ".md")
    if not os.path.exists(note_path):
        return None, f"The file {note_path} does not exist."

    try:
        with open(note_path, "r") as file:
            lines = file.readlines()
            content_lines = []
            in_front_matter = False
            for line in lines:
                if line.strip() == "---":
                    in_front_matter = not in_front_matter
                    continue
                if not in_front_matter:
                    content_lines.append(line)
            headings = []
            heading_pattern = re.compile(r"^(#{1,6})\s+(.*)")
            for line in content_lines:
                match = heading_pattern.match(line)
                if match:
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    if title:
                        headings.append((level, title))
            toc = defaultdict(dict)

            def add_to_toc(toc, level, title):
                if level == 1:
                    toc[title] = {}
                else:
                    for key in toc:
                        add_to_toc(toc[key], level - 1, title)

            for level, title in headings:
                add_to_toc(toc, level, title)
            return dict(toc), None
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
