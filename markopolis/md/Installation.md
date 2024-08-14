Installation has two parts. Server deployment and local setup. The server deployment
is for deploying and setting up the API server and front-end. The local setup is
for pushing markdown files to the server for publishing.

## Deployment using Docker

Use the provided docker-compose:
Fill up the environment values. Make sure to generate and add a secure `API_KEY`.
Allocate persistent storage for the Markdown files.

### Docker Compose
```
version: '3.8'

services:
  markopolis:
    image: ghcr.io/rishikanthc/markopolis:0.1.4
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

### Home Page
The home page content is loaded from a file called `home.md`.
