from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Error(BaseModel):
    message: str


class NoteSearch(BaseModel):
    matches: list[str]


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
    custom_fields: Dict[str, str] = Field(default_factory=dict)


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
