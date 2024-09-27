---
title: API overview
date: 22-09-2024
tags:
  - api
  - backend
publish: true
---

This section details the core operations of the app, specifically the backend.
The backend exposes various REST API endpoints which can serve different types of requests related
to markdown files. Below we detail each of them.

## Overview
This document provides an overview of the API endpoints for the Marco Polo's application. The application is built using SvelteKit for the backend API and PocketBase for the database. A Python package is also used to expose a CLI for uploading files to the server.
## Endpoints
### Upload API

> [!important]
> **Endpoint:** ==/api/upload==
> **Method:** *POST*

- **Description** Uploads markdown files to the server, sets up the database, parses HTML, and stores the compiled results and original files in the database.
- **Parameters**
  - `file`: The markdown file to be uploaded.
  - `url`: Absolute path of file from root of vault.

#### Details

Refer [[Markdown Rendering]]

---
### LS API
- **Endpoint** `/api/ls`
- **Method** GET
- **Description** Builds a file tree from the URL field in each record of the MDBase collection.
- **Responses**:
  - `200 OK`: Returns a JSON response with the file tree.
  - `500 Internal Server Error`: Error in processing the request.
---
### Search API
- **Endpoint** `/api/search`
- **Method** GET
- **Description** Performs a fuzzy search through the content stored in the database.
- **Parameters**:
  - `query`: The search query string.
- **Responses**:
  - `200 OK`: Returns search results with snippets containing matches.
  - `404 Not Found`: No matches found.
---
### Links API
- **Endpoint** `/api/links`
- **Method** GET
- **Description** Retrieves all links and backlinks for a given markdown file.
- **Parameters**
  - `url`: The URL of the markdown file.
- **Responses**
  - `200 OK`: Returns forward and backward links.
  - `404 Not Found`: File not found.
---
### Backlinks API
- **Endpoint** `/api/backlinks`
- **Method** GET
- **Description** Retrieves only the backlinks for a given markdown file.
- **Parameters**
  - `url`: The URL of the markdown file.
- **Responses**:
  - `200 OK`: Returns backlinks.
  - `404 Not Found`: File not found.
---
### Image API
- **Endpoint** `/api/image`
- **Method** GET
- **Description**: Fetches images from the database.
- **Parameters**
  - `url`: The URL of the image file.
- **Responses**:
  - `200 OK`: Returns the image file.
  - `404 Not Found`: Image not found.
