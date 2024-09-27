---
title: Usage
date: 09-24-2024
---

Initially the app starts with an empty database as there are no notes. So we
will begin by uploading some notes.

### Uploading files to server

Open a terminal and `cd` to the root directory of your notes vault. This is the directory
of your notes. Then run `mdsync` in the vault directory. The command will scan for
all markdown and image files.

> [!note]
> You can delete files on the server by simply deleting the file locally in your
> vault and then running `mdsync` command.


### WikiLinks and Images

Markopolis supports Obsidian style WikiLinks and Images. Previously
Markopolis only supported absolute path from note vault. However, from 3.0.0
Markopolis now supports relative path as well.


> [!Tip]
> Checkout [[Markdown Syntax]] to see how different markdown syntax renders.
