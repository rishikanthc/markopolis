import os
import yaml
import requests
import base64
from typing import Dict, Tuple, Optional, List
import logging
from tqdm import tqdm
import hashlib
import fire

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".png", ".jpeg", ".jpg", ".svg", ".gif"}


def parse_frontmatter(content: str) -> Optional[Dict[str, any]]:
    """Parse the frontmatter from a markdown file."""
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def read_markdown_file(file_path: str) -> str:
    """Read the content of a markdown file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_image_file(file_path: str) -> str:
    """Read and encode the content of an image file to base64."""
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_file_hash(content: str) -> str:
    """Generate a hash of the file content."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def get_remote_content(api_url: str, api_key: str, path: str) -> Tuple[str, bool]:
    """Get the content of a file from the server."""
    try:
        response = requests.get(
            f"{api_url}/notes/{path}/raw", headers={"X-API-Key": api_key}
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("contents", "")

        # Check if the content is an error message
        if content.startswith("Error:") or content.startswith("Unexpected error:"):
            return "", False
        return content, True
    except requests.RequestException as e:
        logger.error(f"Error getting remote content for {path}: {str(e)}")
        return "", False


def check_server_status(api_url: str, api_key: str) -> bool:
    """Check if the server is running and accessible."""
    try:
        response = requests.get(f"{api_url}/hello", headers={"X-API-Key": api_key})
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def get_files_by_extension(folder_path: str, extensions: set) -> List[str]:
    """Recursively get all files with the specified extensions in the given folder."""
    files = []
    for root, _, files_in_dir in os.walk(folder_path):
        for file in files_in_dir:
            if os.path.splitext(file)[1].lower() in extensions:
                files.append(os.path.join(root, file))
    return files


def get_markdown_files(folder_path: str) -> List[str]:
    """Recursively get all markdown files in the given folder and its subfolders."""
    return get_files_by_extension(folder_path, {".md"})


def get_image_files(folder_path: str) -> List[str]:
    """Recursively get all image files in the given folder and its subfolders."""
    return get_files_by_extension(folder_path, IMAGE_EXTENSIONS)


def consume(path: str = "."):
    """
    Consume markdown files and publish to server, and upload images.

    :param path: Path to the folder containing markdown files and images (default: current directory)
    """
    # Import settings here to avoid circular imports
    from markopolis import settings

    # Use settings for API URL and API key
    api_url = settings.domain
    api_key = settings.api_key
    folder_path = path

    # Check if the server is running
    if not check_server_status(api_url, api_key):
        logger.error(
            f"Unable to connect to the server at {api_url}. Please ensure the server is running."
        )
        return

    to_publish: Dict[str, str] = {}
    files_without_frontmatter: List[str] = []
    images_to_upload: Dict[str, str] = {}

    # Get list of markdown files in the specified folder and its subfolders
    md_files = get_markdown_files(folder_path)
    image_files = get_image_files(folder_path)

    # Process markdown files
    for file_path in tqdm(md_files, desc="Processing markdown files", unit="file"):
        local_content = read_markdown_file(file_path)

        frontmatter = parse_frontmatter(local_content)
        if frontmatter is None:
            files_without_frontmatter.append(file_path)
            logger.warning(
                f"File {file_path} does not have valid frontmatter. Skipping."
            )
            continue

        if frontmatter.get("publish", False):
            logger.info(f"File {file_path} has 'publish: true' in frontmatter.")
            # Create relative path from the base folder
            relative_path = os.path.relpath(file_path, folder_path)
            # Remove .md extension for the key
            title = os.path.splitext(relative_path)[0]

            # Get remote content
            remote_content, success = get_remote_content(api_url, api_key, title)

            if success:
                # Compare local and remote content
                if get_file_hash(local_content) != get_file_hash(remote_content):
                    to_publish[title] = local_content
                    logger.info(
                        f"File {relative_path} marked for publishing (updated)."
                    )
                else:
                    logger.info(f"File {relative_path} is up to date. Skipping.")
            else:
                # If we couldn't get the remote content, assume it's a new file
                to_publish[title] = local_content
                logger.info(
                    f"File {relative_path} marked for publishing (new or unable to fetch remote content)."
                )
        else:
            logger.info(
                f"File {file_path} does not have 'publish: true' in frontmatter. Skipping."
            )

    # Process image files
    for image_path in tqdm(image_files, desc="Processing image files", unit="file"):
        try:
            relative_path = os.path.relpath(image_path, folder_path)
            img_data = read_image_file(image_path)
            images_to_upload[relative_path] = img_data
            logger.info(f"Image {relative_path} marked for uploading.")
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {str(e)}")

    # Publish markdown files
    if to_publish:
        payload = {"notes": to_publish}

        try:
            with tqdm(
                total=len(to_publish), desc="Uploading markdown files", unit="file"
            ) as pbar:
                response = requests.put(
                    f"{api_url}/notes/write",
                    json=payload,  # Send the correctly formatted payload
                    headers={"Content-Type": "application/json", "X-API-Key": api_key},
                )
                response.raise_for_status()
                pbar.update(len(to_publish))  # Update progress bar after uploading
            logger.info(f"Successfully published {len(to_publish)} markdown files.")
        except requests.RequestException as e:
            logger.error(f"Error sending markdown data to the backend: {str(e)}")
            if e.response is not None and e.response.status_code == 422:
                logger.error(f"Validation error details: {e.response.text}")
    else:
        logger.info("No markdown files need updating.")

    # Upload images
    if images_to_upload:
        payload = {"images": images_to_upload}

        try:
            with tqdm(
                total=len(images_to_upload), desc="Uploading images", unit="file"
            ) as pbar:
                response = requests.put(
                    f"{api_url}/notes/images/upload",
                    json=payload,
                    headers={"Content-Type": "application/json", "X-API-Key": api_key},
                )
                response.raise_for_status()
                pbar.update(
                    len(images_to_upload)
                )  # Update progress bar after uploading
            logger.info(f"Successfully uploaded {len(images_to_upload)} images.")
        except requests.RequestException as e:
            logger.error(f"Error sending image data to the backend: {str(e)}")
            if e.response is not None and e.response.status_code == 422:
                logger.error(f"Validation error details: {e.response.text}")
    else:
        logger.info("No images need uploading.")

    if files_without_frontmatter:
        logger.warning(
            f"The following files were skipped due to missing or invalid frontmatter: {', '.join(files_without_frontmatter)}"
        )


if __name__ == "__main__":
    fire.Fire(consume)
