from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class Conversation(Base, CommonMixin):
    __tablename__ = "conversations"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    kind = Column(String(50), default="general", nullable=False)  # 'general', 'application_agent'
    status = Column(String(50), default="active", nullable=False)  # 'active', 'archived'
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base, CommonMixin):
    __tablename__ = "messages"

    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text", nullable=False)  # 'text', 'application_draft', 'profile_cards'
    sources = Column(JSON, default=list, nullable=False)
    profile_cards = Column(JSON, default=list, nullable=False)
    application_draft_id = Column(String(36), nullable=True)
    feedback = Column(Integer, nullable=True)  # 1 (thumbs up), -1 (thumbs down)
    is_incomplete = Column(Integer, default=0, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class Notification(Base, CommonMixin):
    __tablename__ = "notifications"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 'application_received', 'application_approved', 'application_rejected', 'system'
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    application_id = Column(String(36), nullable=True)

    user = relationship("User", back_populates="notifications")


class Feedback(Base, CommonMixin):
    __tablename__ = "feedback"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True)
    rating = Column(Integer, nullable=False)  # 1 or -1
    comment = Column(Text, nullable=True)
