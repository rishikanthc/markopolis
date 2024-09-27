---
title: Hi,
date: 09-23-2024
---

Welcome to Markopolis, a self-hostable web app and API for managing Markdown knowledge gardens.
Markopolis renders markdown notes as `html` and exposes APIs for interacting with markdown files
to implement a custom eco system around your notes.
TLDR: Self-hosted version of Obsidian publish with future promises

> Self-hostable Obsidian Publish

## Why
Markdown files are my preferred choice for storing information. It's simple and is future proof.
Having used Obsidian and liking it a lot, I moved back to using my text editor as Obsidian was
too distracting. The customizability is endless and I found myself frequently caught down rabbit
holes, trying to optimize for the perfect setup. I had to end the insanity.

I have been using Markdown-Oxide along with my editor and that keeps it super simple. However, I
miss some of the features offered by Obsidian via plugins like 1-click Publish, auto-tagging,
notes discovery, etc. I decided to build something that would help me to easily publish my notes
online, and can be self-hosted on my own hardware. This got me thinking about using REST APIs as
an interface to work with markdown files. That way, I can implement my own features around my notes.
Hence, Markopolis.

## Features

- **Easy setup** Extremely simple to deploy and use
- **Easy publish** Publish notes online with a single command
- **Markdown API interface** Interact with aspecs of markdown using REST APIs
- **Extensible** Extendable using exposed APIs
- **Instand rendering** Article is available online as soon as ypu publish
- **Full text search** Fuzzy search across your entire notes vault
- **Obsidian markdown flavor** Maintains compatibility with obsidian markdown syntax. Supports
  callouts, equations, code highlighting etc.
- **Dark & Light modes** Supports toggling between light and dark themes
- **Easy maintenance** Requires very little to no maintenance
- **Docker support** Available as docker images to self host

## Demo

This website is hosted using Markopolis and is a live demo. These notes are used to demonstrate
the various aspects of Markopolis. Checkout the [[Markdown Syntax]] page for a full showcase
of all supported markdown syntax.

## About me
Hi,
I'm [Rishi](https://rishikanth.me), a recent PhD graduate and soon to start as an Applied Researcher.
I'm an avid self-hoster and a strong proponent of open-source software. I'm based
out of Washington and enjoy solving practical problems with code.
