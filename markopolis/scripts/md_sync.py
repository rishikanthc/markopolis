import os
import yaml
import requests
import base64
import logging
from tqdm import tqdm
import fire
from markopolis.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Helper function to flatten the file tree from the server into a list of file paths
def flatten_file_tree(folder, path=""):
    files = []
    for member in folder["members"]:
        if "folder_name" in member:
            # It's a folder, recursively flatten it
            files.extend(
                flatten_file_tree(
                    member, path=os.path.join(path, member["folder_name"])
                )
            )
        else:
            # It's a file, add to the list
            files.append(os.path.join(path, member["filename"]))
    return files


def mdsync(path="."):
    api_url = settings.domain
    api_key = settings.api_key

    # Supported image formats
    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    # Initialize lists to collect markdown and image file paths
    md_files = []
    image_files = []

    # Walk through the directory to find all markdown and image files
    for root, _, files in os.walk(path):
        for file in files:
            # Collect markdown files
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
            # Collect image files based on their extensions
            elif any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

    # Processing markdown files
    with tqdm(
        total=len(md_files), desc="Processing markdown files", unit="file"
    ) as pbar_md:
        for md_file in md_files:
            try:
                # Read the markdown file content
                with open(md_file, "r") as f:
                    content = f.read()

                # Split the content by lines and check for frontmatter
                content_lines = content.splitlines()

                # Check if the file has valid YAML frontmatter
                if content_lines[0] == "---":
                    end_of_yaml = content_lines[1:].index("---") + 1
                    yaml_frontmatter = "\n".join(content_lines[1:end_of_yaml])
                    parsed_yaml = yaml.safe_load(yaml_frontmatter)

                    # Check if 'publish' is set to true
                    if parsed_yaml.get("publish"):
                        # Prepare the payload for the API request
                        file_path_relative = os.path.relpath(md_file, start=path)
                        payload = {
                            "file_path": file_path_relative,
                            "file_content": content,
                        }

                        # Send the PUT request to the markdown API endpoint
                        response = requests.put(
                            f"{api_url}/api/upload/md",
                            json=payload,
                            headers={"x-api-key": api_key},
                        )

                        # Raise an error if the response was unsuccessful
                        response.raise_for_status()

            except Exception as e:
                # Handle any errors (e.g., invalid frontmatter, API request failure)
                print(f"Error processing file {md_file}: {e}")

            # Update the progress bar
            pbar_md.update(1)

    # Processing image files
    with tqdm(
        total=len(image_files), desc="Processing image files", unit="file"
    ) as pbar_img:
        for img_file in image_files:
            try:
                # Read the image file and encode it as a base64 string
                with open(img_file, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

                # Prepare the payload for the API request
                file_path_relative = os.path.relpath(img_file, start=path)
                payload = {
                    "file_path": file_path_relative,
                    "file_content": encoded_image,
                }

                # Send the PUT request to the image API endpoint
                response = requests.put(
                    f"{api_url}/api/upload/img",
                    json=payload,
                    headers={"x-api-key": api_key},
                )

                # Raise an error if the response was unsuccessful
                response.raise_for_status()

            except Exception as e:
                # Handle any errors (e.g., encoding or API request failure)
                print(f"Error processing image file {img_file}: {e}")

            # Update the progress bar
            pbar_img.update(1)

    # Sync: delete files on the server that are not present locally
    try:
        # Get the list of files from the server
        response = requests.get(
            f"{api_url}/api/notes/ls", headers={"x-api-key": api_key}
        )
        response.raise_for_status()
        server_file_tree = response.json()

        # Flatten the file tree from the server into a list of file paths
        server_files = flatten_file_tree(server_file_tree["root"])
        server_files = [f + ".md" for f in server_files]

        # Flatten the local files
        local_files = [os.path.relpath(f, start=path) for f in md_files + image_files]

        # Identify files that are on the server but not present locally
        files_to_delete = set(server_files) - set(local_files)

        # Delete the files that are no longer present locally
        for file in tqdm(files_to_delete, desc="Deleting server files", unit="file"):
            try:
                # Send the DELETE request to the API
                response = requests.delete(
                    f"{api_url}/api/{file.split('.')[0]}/delete",
                    headers={"x-api-key": api_key},
                )
                response.raise_for_status()
            except Exception as e:
                print(f"Error deleting server file {file}: {e}")

    except Exception as e:
        print(f"Error fetching server file list: {e}")


if __name__ == "__main__":
    fire.Fire(mdsync)
