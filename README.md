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

- **Easy setup** Extremely simple to deploy and use
- **Easy publish** Publish notes online with a single command
- **Markdown API interface** Interact with aspecs of markdown using REST APIs
- **Extensible** Extendable using exposed APIs
- **Develop your own frontend** You can use the api calls to get every section of markdown files to design your own frontend
- **Instand rendering** Article is available online as soon as ypu publish
- **Full text search** Fuzzy search across your entire notes vault
- **Obsidian markdown flavor** Maintains compatibility with obsidian markdown syntax. Supports
  callouts, equations, code highlighting etc.
- **Dark & Light modes** Supports toggling between light and dark themes
- **Easy maintenance** Requires very little to no maintenance
- **Docker support** Available as docker images to self host

and lots more to come. Checkout the [roadmap](https://markopolis.app/roadmap) page for planned features.

## Demo
The documentation [website](https://markopolis.app) is hosted using Markopolis and is a live demo.
These notes are used to demonstrate the various aspects of Markopolis.
Checkout the [[Markdown Syntax]] page for a full showcase of all supported markdown syntax. checking out how different markdown syntax is rendered.

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
Installing Markopolis involves two steps. First deploying the server. Second
installing the CLI tool. The CLI tool provides a utility command to upload
your markdown files to the server. The articles are published as soon as
this command is run.

## Server installation

We will be using Docker for deploying Markopolis.
Create a docker-compose and configure environment variables.
Make sure to generate and add a secure `API_KEY`.
Allocate persistent storage for the Markdown files.


Next create a `docker-compose.yaml` file with the following:

```yaml
version: '3.8'

services:
  markopolis:
    image: ghcr.io/rishikanthc/markopolis:latest
    ports:
      - "8080:8080"
      - "3000:3000"
    environment:
      - POCKETBASE_URL=http://127.0.0.1:8080
      - API_KEY=test
      - POCKETBASE_ADMIN_EMAIL=admin@admin.com
      - POCKETBASE_ADMIN_PASSWORD=password
      - TITLE=Markopolis
      - CAP1=caption1
      - CAP2=caption2
      - CAP3=caption3
    volumes:
      - ./pb_data:/app/db
```

Now you can deploy Markopolis by running `docker-compse up -d`

Parameter | Description
-- | --
POCKETBASE_URL | **DO NOT Change this**
POCKETBASE_ADMIN_EMAIL | The admin account email for the database
POCKETBASE_ADMIN_PASSWORD | The admin account password
TITLE | SITE TITLE
API_KEY | For security, most of the API endpoints are protected by an API key. Make sure to use a secure API key and don't share it publicly.
CAP1 | Caption 1, text that appears below the site title
CAP2 | Caption 2
CAP3 | Caption 3


## Local Installation
Requirements: Python 3.12

Install:
```sh
pip install markopolis
```

### Configuration:
Create a config file as a YAML file in any location.
Set the `MARKOPOLIS_CONFIG_PATH` environment variable to point to the location of the config file.
The config file should specify the domain of the deployment including the protocol and
the api key. The api key should be the same as what you used for the deployment:

```yaml
domain: "https://your-domain.com"
```

I recommend using a python virtual environment for the local installation.


> [!warning]
> the domains should not contain a leading slash at the end.
> For eg. https://example.com will work
> https://example.com/ will not work

## STEP 2: Local installation

I highly recommend configuring a virtual environment for python to keep your environment clean and
and prevent any dependency issues. Below I detail the steps to do this using Conda or pip. If you are familar
with this feel free to skip to the package installation section.

> [!info]
> You need to have python version >= 3.12

### Setting up a virtual environment

You can use either `pip` or `conda` to do this. If you are using `pip` simply run
```bash
python3.12 -m venv <name>
```

Replace `<name>` with your desired virtual environment name. You can then activate the virtual environment
using:
```bash
source <name>
```

For conda, you can use
```bash
conda create -n <name> python==3.12
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

Set the environment variables `MARKOPOLIS_DOMAIN` and `MARKOPOLIS_API`

**bash or zsh (temporarily for current session)**
```bash
export MARKOPOLIS_DOMAIN=https://markopolis.example.com
```

**bash or zsh (permanently for all sessions)**
```bash
echo 'export MARKOPOLIS_DOMAIN=https://markopolis.example.com' >> ~/.zshrc
echo 'export MARKOPOLIS_DOMAIN=https://markopolis.example.com' >> ~/.bashrc

source ~/.zshrc
source ~/.bashrc
```

**fish (temporarily for current session)**
```fish
set -x MARKOPOLIS_DOMAIN https://markopolis.example.com
```


**fish (permanently for all sessions)**
```fish
echo 'set -x MARKOPOLIS_DOMAIN "https://markopolis.example.com"' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

For more information on how to use Markopolis checkout the [Markopolis](https://markopolis.app) website.
If you like this project please considering starring it.
