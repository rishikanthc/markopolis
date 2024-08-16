import os
import yaml
import re
import base64
import requests
from tqdm import tqdm
from loguru import logger
import sys
from markopolis.config import settings
import fire
from pydantic import BaseModel

# Logger setup
logger.remove()
logger.add(sys.stdout, level="DEBUG")


class FileItem(BaseModel):
    title: str
    link: str


class FolderItem(BaseModel):
    folder: str
    members: "list[FileItem | FolderItem]"


class MarkdownFileList(BaseModel):
    files: list[FolderItem]


def valid_yaml_frontmatter(content, file_path):
    """Check if content has valid YAML frontmatter and contains 'publish: true'."""
    if content.strip().startswith("---"):
        frontmatter_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            if frontmatter.get("publish") is True:
                return frontmatter.get(
                    "title", os.path.basename(file_path).replace(".md", "")
                )
    return None


def scan_files(path):
    """Scan for markdown files with valid frontmatter and publish: true."""
    matching_files = {}
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                    title = valid_yaml_frontmatter(content, file_path)
                    if title:
                        # Use file path as the key to ensure uniqueness
                        matching_files[file_path] = file_path
    return matching_files


def scan_images(path):
    """Scan for images with jpg, jpeg, png, webp, svg extensions."""
    image_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".svg")):
                image_files.append(os.path.join(root, file))
    return image_files


def send_file(file_path, api_url, api_key):
    """Send the markdown file to the API endpoint."""
    with open(file_path, "r") as f:
        content = f.read()

    # Use the filename (without .md extension) instead of the frontmatter title for the upload
    title = os.path.basename(file_path).replace(".md", "")

    # Construct the full API URL
    url = f"{api_url}/notes/write"

    # Prepare the payload and headers
    payload = {
        "title": title,  # Filename is used as the title here
        "path": os.path.dirname(os.path.relpath(file_path)),
        "content": content,
    }

    headers = {
        "x-api-key": api_key  # Correct the header key
    }

    # Send the PUT request
    response = requests.put(url, json=payload, headers=headers)
    return response.status_code, response.text


def send_image(image_path, api_url, api_key):
    """Send the image file to the API endpoint."""
    with open(image_path, "rb") as image_file:
        encoded_img = base64.b64encode(image_file.read()).decode("utf-8")

    # Construct the full API URL
    url = f"{api_url}/notes/images/upload"

    # Prepare the payload and headers
    payload = {
        "filename": os.path.basename(image_path),
        "path": os.path.dirname(os.path.relpath(image_path)),
        "img": encoded_img,
    }

    headers = {"x-api-key": api_key}

    # Send the PUT request for the image
    response = requests.put(url, json=payload, headers=headers)
    return response.status_code, response.text


def fetch_server_files(api_url, api_key):
    """Fetch the list of markdown files on the server."""
    url = f"{api_url}/notes/ls"
    headers = {"x-api-key": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return MarkdownFileList(**response.json())
    else:
        logger.error(f"Failed to fetch server files: {response.text}")
        return None


def delete_file_on_server(title, api_url, api_key):
    """Delete the file on the server based on the title."""
    formatted_title = title.replace(" ", "-")
    url = f"{api_url}/notes/{formatted_title}/delete"
    headers = {"x-api-key": api_key}
    response = requests.delete(url, headers=headers)
    return response.status_code, response.text


def md_sync(path="."):
    api_url = settings.domain
    api_key = settings.api_key

    # Step 1: Scan for local markdown files
    logger.debug("Scanning for markdown files...")
    local_files = scan_files(path)

    # Step 2: Fetch server markdown files
    logger.debug("Fetching markdown files from the server...")
    server_files_data = fetch_server_files(api_url, api_key)
    if not server_files_data:
        logger.error("Failed to retrieve server files, aborting sync.")
        return

    # Flatten the server file structure into a simple list of titles
    def flatten_files(folders):
        file_titles = []
        for item in folders:
            if isinstance(item, FolderItem):
                file_titles.extend(flatten_files(item.members))
            elif isinstance(item, FileItem):
                file_titles.append(item.title)
        return file_titles

    server_files = flatten_files(server_files_data.files)

    # Step 3: Delete server files that don't exist locally
    logger.debug("Checking for files to delete on the server...")
    for server_title in server_files:
        if server_title not in local_files:
            status_code, response_text = delete_file_on_server(
                server_title, api_url, api_key
            )
            if status_code == 200:
                logger.debug(f"Successfully deleted {server_title} from server")
            else:
                logger.error(f"Failed to delete {server_title}: {response_text}")

    # Step 4: Upload new/modified markdown files
    logger.debug("Uploading markdown files...")
    with tqdm(
        total=len(local_files), desc="Uploading markdown files", unit="file"
    ) as pbar:
        for file_path in local_files.values():
            status_code, response_text = send_file(file_path, api_url, api_key)
            pbar.update(1)
            if status_code != 200:
                logger.error(f"Failed to upload {file_path}: {response_text}")
            else:
                logger.debug(f"Successfully uploaded {file_path}")

    logger.info(f"Completed uploading {len(local_files)} markdown files")

    # Step 5: Scan for images
    logger.debug("Scanning for images...")
    image_files = scan_images(path)

    # Step 6: Upload images
    with tqdm(total=len(image_files), desc="Uploading images", unit="image") as pbar:
        for image_path in image_files:
            status_code, response_text = send_image(image_path, api_url, api_key)
            pbar.update(1)
            if status_code != 200:
                logger.error(f"Failed to upload {image_path}: {response_text}")
            else:
                logger.debug(f"Successfully uploaded {image_path}")

    logger.info(f"Completed uploading {len(image_files)} images")


if __name__ == "__main__":
    fire.Fire(md_sync)
