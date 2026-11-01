from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class MessageSourceOut(BaseModel):
    title: str
    category: str
    url: str
    snippet: str
    rank: int
    score: float


class MessageOut(BaseModel):
    id: str
    chatId: str
    role: str
    content: str
    contentType: str
    createdAt: str
    sources: List[Dict[str, Any]] = []
    profileCards: List[Dict[str, Any]] = []
    applicationDraftId: Optional[str] = None
    feedback: Optional[int] = None
    isIncomplete: bool = False


class ChatOut(BaseModel):
    id: str
    userId: str
    title: str
    kind: str
    status: str
    createdAt: str
    lastMessageAt: str


class MessageCreate(BaseModel):
    content: str
    chatId: Optional[str] = None


class FeedbackCreate(BaseModel):
    rating: int  # 1 or -1
    comment: Optional[str] = None


class NotificationOut(BaseModel):
    id: str
    userId: str
    type: str
    title: str
    body: str
    readAt: Optional[str] = None
    createdAt: str
    applicationId: Optional[str] = None
