from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional, Any


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
    link: str


class Folder(BaseModel):
    folder_name: str
    members: "List[File | Folder]"


class FileTree(BaseModel):
    root: Folder
