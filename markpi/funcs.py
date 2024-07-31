from typing import Union
from .data_dantic import (
    NoteTitle,
    NoteMeta,
    NoteContent,
    Note,
    ToCItem,
    ToC,
    Backlink,
    BacklinkList,
    MarkdownFileList,
)
from .md import (
    list_markdown_files,
    get_meta,
    get_note_content,
    get_toc,
    get_backlinks_slow,
)


def list_markdown_files_wrapper() -> Union[MarkdownFileList, str]:
    files, error = list_markdown_files()
    if error:
        return error
    return MarkdownFileList(files=files)


def get_note_wrapper(note_title: str) -> Union[Note, str]:
    meta_dict, meta_error = get_meta(note_title)
    if meta_error:
        return f"Error getting metadata: {meta_error}"

    content, content_error = get_note_content(note_title)
    if content_error:
        return f"Error getting note content: {content_error}"

    markdown_content, html_content = content

    meta = NoteMeta(
        title=meta_dict.get("title", note_title),
        date=meta_dict.get("date"),
        tags=meta_dict.get("tags", []),
        custom_fields={
            k: v for k, v in meta_dict.items() if k not in ["title", "date", "tags"]
        },
    )

    return Note(
        title=NoteTitle(value=note_title),
        meta=meta,
        content=NoteContent(markdown=markdown_content, html=html_content),
    )


def get_toc_wrapper(note_title: str) -> Union[ToC, str]:
    toc_dict, error = get_toc(note_title)
    if error:
        return f"Error getting table of contents: {error}"

    def dict_to_toc_item(d: dict) -> ToCItem:
        if not d:
            return ToCItem(title="", children={})
        title = next(iter(d))
        children = d[title]
        return ToCItem(
            title=title,
            children={k: dict_to_toc_item(v) for k, v in children.items()},
        )

    toc_items = {k: dict_to_toc_item({k: v}) for k, v in toc_dict.items()}
    return ToC(headings=toc_items)


def get_backlinks_wrapper(note_title: str) -> Union[BacklinkList, str]:
    backlink_files, error = get_backlinks_slow(note_title)
    if error:
        return f"Error getting backlinks: {error}"

    backlinks = [
        Backlink(title=file.replace(".md", ""), link=file) for file in backlink_files
    ]
    return BacklinkList(backlinks=backlinks)
