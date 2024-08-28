## Introduction
Hi,
I’m [Rishikanth](https://rishikanth.me), and I’m excited to introduce you to Markopolis! It’s a web app and API server I
built that lets you easily share your Markdown notes as websites while giving you full control to
interact with and manage your Markdown files via a powerful API. Just point Markopolis to a folder
with your Markdown files, and it’ll handle the rest. The idea is to help you create your own tools
and features around your notes without being tied down by proprietary systems. It’s completely
open-source and free under the MIT License. Check out the [GitHub repo](https://github.com/rishikanthc/markopolis) and start exploring!

**TLDR:** Self-hosted Obsidian publish with an API to extend functionality.

## Features
- **Simple Deployment:** Extremely easy to deploy, configure, and use.
- **REST API Interface:** Provides a REST API to interact with different Markdown elements in your notes.
- **Customizable UI:** Supports "bring your own user interface" by using Markopolis as a backend.
- **Obsidian Markdown Flavor:** Stays close to the Obsidian Markdown flavor and supports backlinks, todos, LaTeX equations, code, tables, callouts etc.
- **Instant Rendering:** Uses a single command to push Markdown notes to the server and instantly renders them as simple webpages.
- **Full Text Search:** Implements full text search.
- **Dark and Light Modes:** Supports both dark and light modes.
- **Low Maintenance:** Requires very little to no maintenance.
- **Docker Support:** Comes as a deployable Docker image.
- **API Documentation:** Inbuilt API documentation generated using FastAPI.

and lots more to come. Checkout the [roadmap](https://markopolis.app/roadmap) page for planned features.

## Demo
The documentation [website](https://markopolis.app) is hosted using Markopolis and showcases a small collection of Markdown notes to highlight the essential features.
I have tried to incorporate content here to showcase different features. Take a look at the [https://markopolis.app/](https://markopolis.app/Markdown%20Syntax) page for
checking out how different markdown syntax is rendered.

Thank you for considering Markopolis for your Markdown note-sharing needs! If you like
the project considering starring the repository.

## Versioning

I try to follow semantic versioning as much as possible. However, I have still not
streamlined the process yet, so please bear with me if there are any mishaps. v2.0.0 achieves
code separation between backend and frontend because of which I had to fast forward the
docker versioning to match the python package. Going forward I'll try to avoid such mishaps
and I'll be maintaining a detailed changelog at [changelog](https://markopolis.app/changelog).

This is my first open-source project and I'm excited to scale it well. I started building this
mostly out of my personal need, but if there's public interest I'm more than happy to
accept feature requests and contributions. Any and all feedback is welcome. This project
will always be open-source and maintained as I rely on it for my own notes system.

If you like the project please don't forget to star the [github repo](https://github.com/rishikanthc/markopolis.git).

## Installation
Installing Markopolis involves two steps.

- **STEP 1:** Deploying the Markopolis server
- **STEP 2:** Installing the Markopolis package on your local machine

## STEP 1: Deploying Markopolis server

The easiest way to deploy the server is to use the provided docker image.
The docker image packages both the backend and frontend together and sets up a
reverse proxy to route requests correctly to the backend and frontend.

You can use the docker-compose provided below. Make sure to change the
environment variables to match your settings.

> [!warning]
> Make sure to use a secure API key. You can use `openssl rand -hex 32` to
> generate a random alphanumeric string to use as your API key.

### Docker Compose


```
version: '3.8'

services:
  markopolis:
    image: ghcr.io/rishikanthc/markopolis:2.0.0
    ports:
      - "8080:80"
    environment:
      - MARKOPOLIS_DOMAIN="https://your-domain.com"
      - MARKOPOLIS_FRONTEND_URL = https://your-domain.com"
      - MARKOPOLIS_TITLE="Awesome Notes"
      - MARKOPOLIS_MD_PATH=/app/markdown
      - MARKOPOLIS_API_KEY=<really long random alpha-numeric string>
    volumes:
      - markopolis_data:/app/markdown
    restart: unless-stopped

volumes:
  markopolis_data:
    driver: local
```


Parameter | Description
-- | --
MARKOPOLIS_DOMAIN | This is the domain at which both your frontend and backend is available by default. Make sure to include the protocol along with your domain
MARKOPOLIS_FRONTEND_URL | This parameter is available for configuring custom frontend implementations. If you are using the default front-end that ships with Markopolis, this should be **same as MARKOPOLIS_DOMAIN**.
MARKOPOLIS_TITLE | This parameter controls the site title displayed on the top-left in the header
MARKOPOLIS_MD_PATH | This is the path on the server at which your markdown files are stored. Ideally this should point to a directory in your persistent volume.
MARKOPOLIS_API_KEY | For security, most of the API endpoints are protected by an API key. Make sure to use a secure API key and don't share it publicly.

> [!warning]
> the domains should not contain a leading slash at the end.
> For eg. https://example.com will work
> https://example.com/ will not work

## STEP 2: Local installation

Markopolis provides an easy way to sync or push your markdown files from your computer to the server.
You do not need to use Docker to mount your markdown files. Follow the instructions below to set this
up.


I highly recommend configuring a virtual environment for python to keep your environment clean and
and prevent any dependency issues. Below I detail the steps to do this using Conda or pip. If you are familar
with this feel free to skip to the package installation section.

> [!info]
> You need to have python version >= 3.11

### Setting up a virtual environment

You can use either `pip` or `conda` to do this. If you are using `pip` simply run
```bash
python3.11 -m venv <name>
```

Replace `<name>` with your desired virtual environment name. You can then activate the virtual environment
using:
```bash
source <name>
```

For conda, you can use
```bash
conda create -n <name> python==3.11
```

and activate it with
```bash
conda activate <name>
```

### Package installation

Simply install the markopolis python package using your preferred package manager.

**pip:**
```bash
pip install markopolis
```

### Configuration

Create a yaml config file anywhere in your system to set the below values. I recommend
storing it in `.config/markopolis/settings.yaml`.

> [!info]
> You can name the file anything and you can store it anywhere.
> You will need to set the config path for Markopolis to read the config file correctly.

Point markopolis to your config file by setting the `MARKOPOLIS_CONFIG_PATH` to the location
of your yaml file. You can also add it to your shell config so it persists across sessions.


**bash or zsh (temporarily for current session)**
```bash
export MARKOPOLIS_CONFIG_PATH=/path/to/settings.yaml
```

**bash or zsh (permanently for all sessions)**
```bash
echo 'export MARKOPOLIS_CONFIG_PATH=/path/to/settings.yaml' >> ~/.zshrc
echo 'export MARKOPOLIS_CONFIG_PATH=/path/to/settings.yaml' >> ~/.bashrc

source ~/.zshrc
source ~/.bashrc
```

**fish (temporarily for current session)**
```fish
set -x MARKOPOLIS_CONFIG_PATH /path/to/settings.yaml
```


**fish (permanently for all sessions)**
```fish
echo 'set -x MARKOPOLIS_CONFIG_PATH "/path/to/settings.yaml"' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

#### Settings

Below is an example config:

```yaml
default:
  domain: https://your-domain.com
  md_path: /path/to/markdown-notes
  api_key: <really long random alpha-numeric string>
```

Parameter | Description
-- | --
domain | This should point to the markopolis backend deployed. **Same value as MARKOPOLIS_DOMAIN from docker-compose.**
md_path | Local path to where your markdown notes are stored. This is the path on your local machine on which you have your obsidian notes stored.
api_key | The API key you used when deploying the server. **Same as MARKOPOLIS_API_KEY from docker-compose.**

## Testing deployment

Immediately after deployment, since no markdown files have been added, initially the
site will throw an error. To test if the deployment was successful you can navigate
to the API documentation page which is auto-generated and available at `http(s)://your-domain.com/docs`.
This should display a swagger UI with details about all available API endpoints. It would
look exactly like what's shown at [Markopolis API docs](https://markopolis.app/docs)

## Usage

There are a few details users need to be aware to make sure Markopolis
works correctly. Particularly when it comes to maintaing compatibility
with Obsidian eco-system.

## Uploading files to the server
In order to upload files easily to your server, Markopolis provides 2
convenience functions.

### mdsync
Navigate to the root directory of your markdown files and simply run
`mdsync`. This command will upload all markdown and image files to the
server and in addition will **DELETE** any files on the server that are NOT
present in the local directory.

### consume
Navigate to the root directory of your markdown files and run `consume`.
This command will upload all markdown and image files to the server.
This command will **NOT DELETE** files on the server.

> [!info]
> Note that both commands replicate the entire file and directory structure.
> Both commands need to be run from the *root* location for your markdown
> files.

## Homepage
The homepage or root page is loaded from the contents of a markdown file
titled `home.md`. It has to be named exactly as `home.md` without any
capitalization. Without this the homepage will throw an error.


## Display titles
By default, all files and page titles will use the filename. You can
override this by supplying a `title:` field in your yaml frontmatter.
If `title` is provided in the frontmatter, it will be used for display
everywhere. Note that the url will point to the filename though.

## Wikilinks and Images
All wikilnks and image paths should be specified relative to the vault root.
Obsidian has an inbuilt setting to handle this automatically without having
to change your workflows. To configure this, go to `Settings -> Files and links`
and under `New Link Format` choose `Absolute path in vault`
