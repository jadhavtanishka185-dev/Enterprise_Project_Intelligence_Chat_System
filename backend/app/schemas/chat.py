from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ChatRequest(BaseModel):
    question: str


class ChatSource(BaseModel):
    content: str
    document: str
    page: Optional[int] = None


class ChatResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    question: str
    answer: str
    sources: Optional[List[Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True
