from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    file_type: str
    file_size: Optional[int] = None
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
