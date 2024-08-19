from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional, Any


class Status(BaseModel):
    status: int


class MDFile(BaseModel):
    file_path: str
    file_content: str


class ImageFile(BaseModel):
    file_path: str
    file_content: str


class Frontmatter(BaseModel):
    title: str
    date: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class NoteHtml(BaseModel):
    html_content: str


class File(BaseModel):
    filename: str
    title: str
    link: str


class Folder(BaseModel):
    folder_name: str
    members: "List[File | Folder]"


class FileTree(BaseModel):
    root: Folder


class Backlink(BaseModel):
    title: str
    path: str


class Backlinks(BaseModel):
    backlinks: List[Backlink]


class NoteSearch(BaseModel):
    matches: list[str]


class FuzzySearchResult(BaseModel):
    file_path: str
    snippet: str


class NoteSearchFull(BaseModel):
    results: list[FuzzySearchResult]


class ToCItem(BaseModel):
    title: str
    children: Dict[str, "ToCItem"] = Field(default_factory=dict)


class ToC(BaseModel):
    headings: Dict[str, ToCItem]
