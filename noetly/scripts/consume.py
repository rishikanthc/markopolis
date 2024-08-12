import os
import yaml
import requests
from typing import Dict, Tuple, Optional, List
import logging
from tqdm import tqdm
import hashlib
import fire

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def get_file_hash(content: str) -> str:
    """Generate a hash of the file content."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def get_remote_content(api_url: str, api_key: str, title: str) -> Tuple[str, bool]:
    """Get the content of a file from the server."""
    try:
        response = requests.get(
            f"{api_url}/notes/{title}/raw", headers={"X-API-Key": api_key}
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("contents", "")

        # Check if the content is an error message
        if content.startswith("Error:") or content.startswith("Unexpected error:"):
            return "", False
        return content, True
    except requests.RequestException as e:
        logger.error(f"Error getting remote content for {title}: {str(e)}")
        return "", False


def check_server_status(api_url: str, api_key: str) -> bool:
    """Check if the server is running and accessible."""
    try:
        response = requests.get(f"{api_url}/hello", headers={"X-API-Key": api_key})
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def consume(path: str = "."):
    """
    Consume markdown files and publish to server.

    :param path: Path to the folder containing markdown files (default: current directory)
    """
    # Import settings here to avoid circular imports
    from noetly import settings

    # Use settings for API URL and API key
    api_url = settings.backend_url + f":{settings.backend_port}"
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

    # Get list of markdown files in the specified folder
    md_files = [f for f in os.listdir(folder_path) if f.endswith(".md")]

    # Iterate through all files in the specified directory with progress bar
    for filename in tqdm(md_files, desc="Processing files", unit="file"):
        file_path = os.path.join(folder_path, filename)
        local_content = read_markdown_file(file_path)

        frontmatter = parse_frontmatter(local_content)
        if frontmatter is None:
            files_without_frontmatter.append(filename)
            logger.warning(
                f"File {filename} does not have valid frontmatter. Skipping."
            )
            continue

        if frontmatter.get("publish", False):
            logger.info(f"File {filename} has 'publish: true' in frontmatter.")
            # Remove .md extension for the key
            title = os.path.splitext(filename)[0]

            # Get remote content
            remote_content, success = get_remote_content(api_url, api_key, title)

            if success:
                # Compare local and remote content
                if get_file_hash(local_content) != get_file_hash(remote_content):
                    to_publish[title] = local_content
                    logger.info(f"File {filename} marked for publishing (updated).")
                else:
                    logger.info(f"File {filename} is up to date. Skipping.")
            else:
                # If we couldn't get the remote content, assume it's a new file
                to_publish[title] = local_content
                logger.info(
                    f"File {filename} marked for publishing (new or unable to fetch remote content)."
                )
        else:
            logger.info(
                f"File {filename} does not have 'publish: true' in frontmatter. Skipping."
            )

    if to_publish:
        try:
            # Create a new progress bar for uploading files
            with tqdm(
                total=len(to_publish), desc="Uploading files", unit="file"
            ) as pbar:
                response = requests.put(
                    f"{api_url}/notes/write",
                    json=to_publish,
                    headers={"Content-Type": "application/json", "X-API-Key": api_key},
                )
                response.raise_for_status()
                pbar.update(len(to_publish))  # Update progress bar after uploading
            logger.info(f"Successfully published {len(to_publish)} files.")
        except requests.RequestException as e:
            logger.error(f"Error sending data to the backend: {str(e)}")
            logger.error(f"Request URL: {api_url}/notes/write")
            logger.error(f"Request payload: {to_publish.keys()}")
    else:
        logger.info("No files need updating.")

    if files_without_frontmatter:
        logger.warning(
            f"The following files were skipped due to missing or invalid frontmatter: {', '.join(files_without_frontmatter)}"
        )


if __name__ == "__main__":
    fire.Fire(consume)
