from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Error(BaseModel):
    error: str


class Health(BaseModel):
    status: str


class Status(BaseModel):
    status: int


class NoteSearch(BaseModel):
    matches: list[str]


class FuzzySearchResult(BaseModel):
    file_path: str
    snippet: str


class NoteSearchFull(BaseModel):
    results: list[FuzzySearchResult]


class NoteTitle(BaseModel):
    value: str

    @field_validator("value")
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class NoteMeta(BaseModel):
    title: str
    date: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)  # Changed to Any
    path: str


class NoteContent(BaseModel):
    markdown: str
    html: str


class Note(BaseModel):
    title: NoteTitle
    meta: NoteMeta
    content: NoteContent


class ToCItem(BaseModel):
    title: str
    children: Dict[str, "ToCItem"] = Field(default_factory=dict)


class ToC(BaseModel):
    headings: Dict[str, ToCItem]


class Backlink(BaseModel):
    title: str
    link: str


class BacklinkList(BaseModel):
    backlinks: List[Backlink]


class MarkdownFileList(BaseModel):
    files: List[str]


class Raw(BaseModel):
    contents: str


class WriteNotesInput(BaseModel):
    notes: dict[str, str]
