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

# Logger setup
logger.remove()
logger.add(sys.stdout, level="DEBUG")


def valid_yaml_frontmatter(content):
    """Check if content has valid YAML frontmatter and contains 'publish: true'."""
    if content.strip().startswith("---"):
        frontmatter_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            if frontmatter.get("publish") is True:
                return True
    return False


def scan_files(path):
    """Scan for markdown files with valid frontmatter and publish: true."""
    matching_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                    if valid_yaml_frontmatter(content):
                        matching_files.append(file_path)
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

    # Construct the full API URL
    url = f"{api_url}/notes/write"

    # Prepare the payload and headers
    payload = {
        "title": os.path.basename(file_path).replace(".md", ""),
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


def md_sync(path="."):
    api_url = settings.domain
    api_key = settings.api_key

    # Step 1: Scan for markdown files
    logger.debug("Scanning for markdown files...")
    matching_files = scan_files(path)

    # Step 2: Send markdown files
    with tqdm(
        total=len(matching_files), desc="Uploading markdown files", unit="file"
    ) as pbar:
        for file_path in matching_files:
            status_code, response_text = send_file(file_path, api_url, api_key)
            pbar.update(1)
            if status_code != 200:
                logger.error(f"Failed to upload {file_path}: {response_text}")
            else:
                logger.debug(f"Successfully uploaded {file_path}")

    logger.info(f"Completed uploading {len(matching_files)} markdown files")

    # Step 3: Scan for images
    logger.debug("Scanning for images...")
    image_files = scan_images(path)

    # Step 4: Send images
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
