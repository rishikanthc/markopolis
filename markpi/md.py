import os
import yaml
from yaml.constructor import ConstructorError

# Global variable for the directory containing markdown files
MDROOT = "../md-test"

__all__ = ["list_markdown_files", "get_meta"]


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
