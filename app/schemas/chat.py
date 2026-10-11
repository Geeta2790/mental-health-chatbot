from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    answer: str
    sources: list[str] = []


class FeedbackRequest(BaseModel):
    message_id: int
    rating: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    message_id: int
    rating: str