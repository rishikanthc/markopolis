import base64
from loguru import logger
import sys
import re
import regex as mre
import sh
import markdown
from .md_extensions import (
    ImageExtension,
    CalloutExtension,
    MermaidExtension,
    StrikethroughExtension,
    HighlightExtension,
)
from markopolis.config import settings
import yaml
import os
from pathlib import Path
import markopolis.dantic as D

logger.remove()
logger.add(sys.stdout, level="DEBUG")


def extract_title_from_frontmatter(file_path):
    """
    Extract the title from the YAML frontmatter of the markdown file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            frontmatter_match = re.match(
                r"^---\s*\n(.*?\n?)^---\s*\n", content, re.DOTALL | re.MULTILINE
            )
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                yaml_data = yaml.safe_load(frontmatter)
                if "title" in yaml_data:
                    return yaml_data["title"]
    except Exception as e:
        logger.debug(f"Failed to extract title from {file_path}: {e}")
    return None


def write_md_files(md_file_dict):
    try:
        # Extract file path and content from the dictionary
        file_path = md_file_dict["file_path"]
        file_content = md_file_dict["file_content"]

        # Get the root directory from settings
        md_root = settings.md_path

        # Split the file_path into directory and filename
        directory, filename = os.path.split(file_path)

        # Remove the .md extension to use for title if needed
        filename_without_ext = filename[:-3]

        # Construct the full path to the directory by combining md_root and the directory
        full_directory_path = os.path.join(md_root, directory)

        # Ensure the directory exists
        os.makedirs(full_directory_path, exist_ok=True)

        # Parse the YAML frontmatter and check for title
        content_lines = file_content.splitlines()

        # Find where the frontmatter ends
        if content_lines[0] == "---":
            end_of_yaml = content_lines[1:].index("---") + 1
            yaml_frontmatter = "\n".join(content_lines[1:end_of_yaml])
            parsed_yaml = yaml.safe_load(yaml_frontmatter)

            # Check if 'title' exists in the parsed YAML, if not set it to the filename without extension
            if "title" not in parsed_yaml:
                parsed_yaml["title"] = filename_without_ext

            # Add or update the 'markopolis.fpath' field with the relative file path
            if "markopolis" not in parsed_yaml:
                parsed_yaml["markopolis"] = {}
            parsed_yaml["markopolis"]["fpath"] = file_path

            # Rebuild the content with updated YAML frontmatter
            updated_yaml = yaml.dump(parsed_yaml, default_flow_style=False)
            file_content = f"---\n{updated_yaml}---\n" + "\n".join(
                content_lines[end_of_yaml + 1 :]
            )

        # Construct the full path for the file
        full_file_path = os.path.join(full_directory_path, filename)

        # Write the content to the markdown file
        with open(full_file_path, "w") as md_file:
            md_file.write(file_content)

        return 0  # Success
    except Exception as e:
        # Log the error if necessary
        print(f"Error writing markdown file: {e}")
        return -1  # Error


def write_images(img_file_dict):
    try:
        # Extract file path and content from the dictionary
        file_path = img_file_dict["file_path"]
        file_content = img_file_dict["file_content"]

        # Get the root directory from settings
        md_root = settings.md_path

        # Construct the full path by combining md_root and the relative file path
        full_path = os.path.join(md_root, file_path)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Decode the base64 image content
        image_data = base64.b64decode(file_content)

        # Write the decoded image content to the file
        with open(full_path, "wb") as image_file:
            image_file.write(image_data)

        return 0  # Success
    except Exception as e:
        # Log the error if necessary
        print(f"Error writing image file: {e}")
        return -1  # Error


def unsluggify(slug: str) -> str:
    return slug.replace("-", " ")


def get_frontmatter(note_path: str):
    # Unspluggify the note path to convert hyphens back to spaces
    unsluggified_path = unsluggify(note_path)

    # Get the root directory from settings
    md_root = settings.md_path

    # Construct the full path to the markdown file by adding the .md extension
    full_file_path = os.path.join(md_root, f"{unsluggified_path}.md")

    # Check if the file exists
    if not os.path.exists(full_file_path):
        raise FileNotFoundError(f"Note '{unsluggified_path}' not found.")

    # Read the file content
    with open(full_file_path, "r") as md_file:
        content_lines = md_file.readlines()

    # Parse the frontmatter from the markdown file
    if content_lines[0].strip() == "---":
        end_of_yaml = content_lines[1:].index("---\n") + 1
        yaml_frontmatter = "".join(content_lines[1:end_of_yaml])
        parsed_yaml = yaml.safe_load(yaml_frontmatter)

        # Convert to the Frontmatter dataclass structure
        frontmatter = {
            "title": parsed_yaml.get("title", unsluggified_path),
            "date": parsed_yaml.get("date", None),
            "tags": parsed_yaml.get("tags", []),
            "custom_fields": {
                key: value
                for key, value in parsed_yaml.items()
                if key not in ["title", "date", "tags"]
            },
        }

        return frontmatter
    else:
        raise ValueError("Frontmatter not found in the specified markdown file.")


def get_note_html(note_path):
    # Unspluggify the note path to convert hyphens back to spaces
    unsluggified_path = unsluggify(note_path)

    md_configs = {
        "mdx_wikilink_plus": {
            "base_url": f"{settings.domain}",
        },
    }

    # Get the root directory from settings
    md_root = settings.md_path

    # Construct the full path to the markdown file by adding the .md extension
    full_file_path = os.path.join(md_root, f"{unsluggified_path}.md")

    # Check if the file exists
    if not os.path.exists(full_file_path):
        raise FileNotFoundError(f"Note '{unsluggified_path}' not found.")

    # Read the markdown file content
    with open(full_file_path, "r") as md_file:
        content_lines = md_file.readlines()

    # Parse the frontmatter and extract the content
    if content_lines[0].strip() == "---":
        end_of_yaml = content_lines[1:].index("---\n") + 1
        content_lines = content_lines[end_of_yaml + 1 :]  # Ignore the frontmatter

    # Join the content lines into a single markdown string
    markdown_content = "".join(content_lines)

    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            ImageExtension(),
            "mdx_wikilink_plus",
            # WikiLinkExtension(base_url="/", end_url=""),
            "markdown_checklist.extension",
            "markdown.extensions.tables",
            "footnotes",
            StrikethroughExtension(),
            HighlightExtension(),
            MermaidExtension(),
            CalloutExtension(),
            # "mdx_math",
        ],
        extension_configs=md_configs,
    )
    # Convert Markdown to HTML
    html_content = md.convert(markdown_content)

    return html_content


def list_notes() -> D.FileTree:
    md_root = Path(settings.md_path)

    def build_file_tree(root_path: Path, current_path: str = "") -> D.Folder:
        members = []
        folder_name = root_path.name

        if current_path == "":
            updated_path = f"{settings.domain}"
        else:
            updated_path = f"{current_path}/{folder_name}".lstrip("/")

        # List files, extract titles from frontmatter, and sort them by title lexicographically
        files = list(root_path.glob("*.md"))
        file_info = []

        for file in files:
            ftitle = os.path.relpath(file, md_root)
            fpath = os.path.join(md_root, ftitle)

            # Extract title from the frontmatter
            _title = extract_title_from_frontmatter(fpath)
            if _title is None:
                _title = ftitle.split(".")[0]

            file_info.append({"file": file, "title": _title})

        # Sort the files by title
        sorted_files = sorted(file_info, key=lambda x: x["title"])

        for info in sorted_files:
            file = info["file"]
            _title = info["title"]
            file_obj = D.File(
                filename=file.name.split(".")[0],
                link=f"{updated_path}/{file.stem}",
                title=_title,
            )
            members.append(file_obj)

        # Recursively add subfolders and sort them lexicographically
        subfolders = sorted(
            [subfolder for subfolder in root_path.iterdir() if subfolder.is_dir()],
            key=lambda f: f.name,
        )
        for subfolder in subfolders:
            subfolder_obj = build_file_tree(subfolder, updated_path)
            members.append(subfolder_obj)

        return D.Folder(folder_name=folder_name, members=members)

    # Start the recursive process from the root folder
    root_folder = build_file_tree(md_root)

    return D.FileTree(root=root_folder)


def clean_path(path):
    """
    Clean up the path by removing ANSI escape sequences and other non-printable characters.
    """
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", path).strip()


def find_backlinks(target_file):
    pth = settings.md_path
    print(f"Searching for backlinks to: {target_file}")
    print(f"In vault directory: {pth}")

    # The pattern for backlinks in the markdown format [[<filename>]]
    target = target_file.split(".")[0]
    backlink_pattern = rf"\[\[{re.escape(target)}\]\]"

    backlinks_list = []

    try:
        # Use sh.Command to get the full path of rg
        rg = sh.Command("rg")

        # Run ripgrep to search for backlinks
        result = rg("-l", backlink_pattern, pth, _err_to_out=True)

        if result:
            matches = result.splitlines()

            for match in matches:
                # Clean the path
                clean_match = clean_path(match)

                # Get the relative path from the md_path
                relative_path = os.path.relpath(clean_match, pth)

                # Extract title from the YAML frontmatter of the matched markdown file
                title = extract_title_from_frontmatter(clean_match)
                if title:
                    backlink = D.Backlink(title=title, path=relative_path.split(".")[0])
                    backlinks_list.append(backlink)
                else:
                    logger.debug(f"No title found in {clean_match}")

        else:
            logger.debug("No backlinks found.")

    except sh.CommandNotFound:
        logger.debug(
            "Error: ripgrep (rg) command not found. Make sure it's installed and in your PATH."
        )
    except sh.ErrorReturnCode as e:
        logger.debug(f"ripgrep command failed with exit code {e.exit_code}")
        logger.debug("STDOUT:")
        logger.debug(e.stdout.decode())
        logger.debug("STDERR:")
        logger.debug(e.stderr.decode())
    except Exception as e:
        logger.debug(f"An unexpected error occurred: {e}")
        logger.debug(f"Error type: {type(e)}")

    # Create the Backlinks object from the collected backlinks
    backlinks_object = D.Backlinks(backlinks=backlinks_list)
    return backlinks_object


def fuzzy_search_in_text(search_term, max_dist=2):
    """
    Perform a fuzzy search on the contents of files and return matches ordered by closeness.
    """
    logger.info(
        f"Starting fuzzy search for term: {search_term} with max_dist: {max_dist}"
    )
    logger.info(f"MDROOT: {settings.md_path}")

    matches_with_distances = []
    pattern = f"({search_term}){{e<={max_dist}}}"

    try:
        for root, _, files in os.walk(settings.md_path):
            for file_name in files:
                if not file_name.endswith(".md"):
                    continue
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, settings.md_path)

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

        # Format results using data classes
        results = [
            D.FuzzySearchResult(file_path=match[0], snippet=match[1])
            for match in sorted_matches
        ]

        logger.info(f"Total matches found: {len(results)}")
        return D.NoteSearchFull(results=results)
    except Exception as e:
        logger.exception(f"Unexpected error in fuzzy search: {str(e)}")
        return D.NoteSearchFull(results=[])


def get_toc(note_path: str) -> D.ToC:
    if not note_path or not isinstance(note_path, str):
        raise ValueError("Invalid note path")

    full_note_path = os.path.join(settings.md_path, note_path + ".md")
    if not os.path.exists(full_note_path):
        raise FileNotFoundError(f"The file {full_note_path} does not exist.")

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

        # Build TOC using ToCItem data class
        current_levels = {0: D.ToCItem(title="root")}

        for level, title in headings:
            new_item = D.ToCItem(title=title)
            parent_level = max(k for k in current_levels.keys() if k < level)
            current_levels[parent_level].children[title] = new_item
            current_levels[level] = new_item

            # Clear any deeper levels
            for lvl in list(current_levels.keys()):
                if lvl > level:
                    del current_levels[lvl]

        # Wrap result in ToC and return
        return D.ToC(headings=current_levels[0].children)

    except Exception as e:
        raise RuntimeError(f"Error processing file: {e}")
