from datetime import datetime

from pydantic import BaseModel


class GeneratedTextFileBase(BaseModel):
    url: str

    class Config:
        from_attributes = True


class GeneratedTextFileCreate(GeneratedTextFileBase):
    email : str | None


class GeneratedTextFileRead(GeneratedTextFileBase):
    id: int
    created_at: datetime
    file_name: str | None
    completed: bool
    title: str | None


class GeneratedTextFileURL(BaseModel):
    url: str