# Markopolis
Hi,
My name is [Rishikanth](https://rishikanth.me). I built Markopolis, a web app and API server
designed to serve Markdown files. It allows you to share Markdown notes as websites and interact with and manipulate
your Markdown files using an API. Simply install Markopolis, point it to a directory holding
all your Markdown files, and the library takes care of everything else. Markopolis is
open-source and free and is released under the MIT-License. Check out the [github repository](https://github.com/rishikanthc/markopolis).

**TLDR:** Markopolis is a self-hostable alternative to Obsidian Publish

## Why I Built This?
I built Markopolis because I wanted a web server that primarily uses plain text Markdown
files for note-taking. As much as I love the customizability that Obsidian offers, I found
it too distracting and easy to get lost in optimizing and customizing. I wanted a self-hosted
solution for sharing and viewing my Markdown notes online, similar to Obsidian Publish, but
without getting locked into the Obsidian ecosystem. After failing to find an existing solution,
I decided to build my own, and thus Markopolis was born.

## Features
- **Simple Deployment:** Extremely easy to deploy, configure, and use.
- **REST API Interface:** Provides a REST API to interact with different Markdown elements in your notes.
- **Customizable UI:** Supports "bring your own user interface" by using Markopolis as a backend.
- **Obsidian Markdown Flavor:** Stays close to the Obsidian Markdown flavor and supports backlinks, todos, callouts, mermaid diagrams and LaTeX equations.
- **Instant Rendering:** Uses a single command to push Markdown notes to the server and instantly renders them as simple webpages.
- **Full Text Search:** Implements full text search.
- **Dark and Light Modes:** Supports both dark and light modes.
- **Code Formatting and Todos:** Supports code formatting and todos.
- **Low Maintenance:** Requires very little to no maintenance.
- **Docker Support:** Comes as a deployable Docker image.
- **Local Installation:** Can also be installed locally.
- **API Documentation:** Inbuilt API documentation generated using FastAPI.

## Demo
Check out [docs website](https://markopolis.app) for a live demo, which showcases a small collection of Markdown notes to highlight the essential features.
Check out the Installation section for instructions on how to deploy and configure Markopolis.


## Installation
Installation has two parts. Server deployment and local setup. The server deployment
is for deploying and setting up the API server and front-end. The local setup is
for pushing markdown files to the server for publishing.

### Deployment using Docker

Use the provided docker-compose:
Fill up the environment values. Make sure to generate and add a secure `API_KEY`.
Allocate persistent storage for the Markdown files.

#### Docker Compose
```
version: '3.8'

services:
  markopolis:
    image: ghcr.io/rishikanthc/markopolis:1.1.1
    ports:
      - "8080:8080"
    environment:
      - MARKOPOLIS_DOMAIN="https://your-domain.com"
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

Deploy using Docker:

```sh
docker-compose up -d
```


### Local Installation
Requirements: Python 3.12

Install:
```sh
pip install markopolis
```

#### Configuration:
Create a config file as a YAML file in any location.
Set the `MARKOPOLIS_CONFIG_PATH` environment variable to point to the location of the config file.
The config file should specify the domain of the deployment including the protocol and
the api key. The api key should be the same as what you used for the deployment:

```yaml
default:
  domain: "https://your-domain.com"
  api_key: <really long random alpha-numeric string>
```

I recommend using a python virtual environment for the local installation.

## Usage

On the first run, since, there are no markdown files to load, the page will throw an error.
You can verify if installation was successful by navigating to the API documentation
which is generated automatically at `https://your-domain.com/docs`. This should load up
the SwaggerUI for the API endpoints exposed.

### Publishing files
All markdown files you want to publish should have `publish: true` in the frontmatter.
Navigate to the directory containing your markdown notes and simply run `consume`.
This command will scan all markdown files in your folder and upload it to the server.
If the file already exists on the server, then it checks if there are any changes.
If there are no changes, the file is skipped. If there are changes then it is overwritten.

## New Sync Feature
v1.1.0 and up support a new command `mdsync` which syncs your local markdown files with the server.
This command is useful for keeping your local files in sync with the server. It will upload new files
and update existing files. It will also delete files that are no longer present in the local directory.

### Home Page
The home page content is loaded from a file called `home.md`.


## Roadmap
In no particular order, here are some of the features that are planned:

- [x] Support for Obsidian callouts.
- [x] Mermaid diagrams.
- [ ] Editor-agnostic cross-device syncing.
- [x] Delete file API interface.
- [ ] Graph view.
- [ ] Daily notes.
- [ ] Private pages to hide specific pages under a password.
- [ ] Support for integrating Obsidian Publish and syncing.
- [x] Support for rendering Markdown tables.
- [x] Support for images.
- [ ] Better tag handling (view tags as links, collect pages by tags, a page for viewing all tags).
- [ ] Support for DataView queries.


Thank you for considering Markopolis for your Markdown note-sharing needs! If you like
the project considering starring the repository.

## Contributing


Contributions are most welcome. I am looking to add several features
to this project and would appreciate any and all help I can get.
Check out the Roadmap for a list of features I currently plan to implement.

Below are few things I need help with:

- Unit testing
- User feedback
- Obsidian plugin development
- Figuring out the best strategy to implement Sync
- Front-end improvements

Please feel free to connect with me on github by opening an issue or drop an email.
Any and all help is appreciated :)
