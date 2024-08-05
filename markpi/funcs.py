from .data_dantic import (
    NoteSearch,
    NoteMeta,
    NoteContent,
    ToCItem,
    ToC,
    MarkdownFileList,
    Error,
    Backlink,
    BacklinkList,
)
from .md import (
    list_markdown_files,
    get_meta,
    get_note_content,
    get_toc,
    fuzzy_search,
    get_backlinks_slow,
)
from loguru import logger

__all__ = ["list_md", "get_metadata", "get_note", "get_headings"]


def list_md():
    files, error = list_markdown_files()

    if files is not None:
        return MarkdownFileList(files=files)
    elif error is not None:
        return Error(message=error)
    else:
        logger.error("Something bad happened, both files and error was None")


def get_metadata(note_title):
    metadata, error = get_meta(note_title)

    if metadata is not None:
        return NoteMeta(
            title=metadata["title"], date=metadata["date"], tags=metadata["tags"]
        )
    elif error is not None:
        return Error(message=error)
    else:
        logger.error("Something bad happened, both files and error was None")


def get_note(note_title):
    content, error = get_note_content(note_title)

    if content is not None:
        return NoteContent(markdown=content[0], html=content[1])
    elif error is not None:
        logger.error(f"{error}")
        return Error(message=error)
    else:
        logger.error("Something bad happened")


def get_headings(note_title):
    toc, error = get_toc(note_title)

    def create_toc_item(title: str, children: dict) -> ToCItem:
        return ToCItem(
            title=title,
            children={k: create_toc_item(k, v) for k, v in children.items()},
        )

    if toc is not None:
        headings = {k: create_toc_item(k, v) for k, v in toc.items()}
        return ToC(headings=headings)
    elif error is not None:
        return Error(message=error)
    else:
        logger.error("Something bad happened")


def search(query, max_dist):
    matches = fuzzy_search(query, max_dist)
    return NoteSearch(matches=matches)


def get_backlinks(note_title):
    backlinks, error = get_backlinks_slow(note_title)

    if backlinks is not None:
        blinks = [
            Backlink(title=b.split(".")[0].replace("-", " "), link=b.split(".")[0])
            for b in backlinks
        ]
        return BacklinkList(backlinks=blinks)
    elif error is not None:
        return Error(message=error)
