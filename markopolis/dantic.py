from pydantic import BaseModel


class MDFile(BaseModel):
    file_path: str
    file_content: str


class ImageFile(BaseModel):
    file_path: str
    file_content: str
