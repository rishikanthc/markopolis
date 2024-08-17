import base64
from loguru import logger
import sys
import markdown
from .md_extensions import (
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

        # List files and sort them lexicographically
        files = sorted(root_path.glob("*.md"), key=lambda f: f.name)
        for file in files:
            file_obj = D.File(
                filename=file.name.split(".")[0],
                link=f"/{updated_path}/{file.stem}".lstrip("/"),
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
