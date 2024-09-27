---
title: Installation
date: 09-24-2024
tags:
  - install
  - docker
---

Installing Markopolis involves two steps. First deploying the server. Second
installing the CLI tool. The CLI tool provides a utility command to upload
your markdown files to the server. The articles are published as soon as
this command is run.

## Server installation

We will be using Docker for deploying Markopolis.
Create a docker-compose and configuring environment variables.
Make sure to generate and add a secure `API_KEY`.
Allocate persistent storage for the Markdown files.

First create a `.env` file to configure the following environment variables.

```bash
POCKETBASE_URL=http://127.0.0.1:8090
API_KEY=<long alpha-numeric string"
POCKETBASE_ADMIN_EMAIL=test@example.com
POCKETBASE_ADMIN_PASSWORD=1234567890
TITLE=Markopolis
```

Next create a `docker-compose.yaml` file with the following:

```yaml
version: '3.8'

services:
  sveltekit-pocketbase:
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
    volumes:
      - ./pb_data:/app/pb

```

Now you can deploy Markopolis by running `docker-compse up -d`


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

## Post-install
Initially since the server hasn't seen any markdown files the app will throw a 500 Error.
Check [[usage]] for details on how to setup Markopolis
