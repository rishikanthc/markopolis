---
title: Welcome to Markopolis
---

## Introduction
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
- **Obsidian Markdown Flavor:** Stays close to the Obsidian Markdown flavor and supports backlinks, todos, and LaTeX equations.
- **Instant Rendering:** Uses a single command to push Markdown notes to the server and instantly renders them as simple webpages.
- **Full Text Search:** Implements full text search.
- **Dark and Light Modes:** Supports both dark and light modes.
- **Code Formatting and Todos:** Supports code formatting and todos.
- **Low Maintenance:** Requires very little to no maintenance.
- **Docker Support:** Comes as a deployable Docker image.
- **Local Installation:** Can also be installed locally.
- **API Documentation:** Inbuilt API documentation generated using FastAPI.

## Demo
This website is hosted using Markopolis and showcases a small collection of Markdown notes to highlight the essential features.
Check out the [[Installation]] page for instructions on how to deploy and configure Markopolis.

Thank you for considering Markopolis for your Markdown note-sharing needs! If you like
the project considering starring the repository.
