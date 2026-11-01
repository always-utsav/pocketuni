from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user
from backend.app.models.identity import User
from backend.app.models.communication import Conversation, Message, Notification, Feedback
from backend.app.schemas.communication import (
    ChatOut,
    MessageOut,
    MessageCreate,
    FeedbackCreate,
    NotificationOut,
)

router = APIRouter()


@router.get("/chats", response_model=List[ChatOut])
def get_user_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chats = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_deleted == False
    ).order_by(Conversation.updated_at.desc()).all()

    return [
        ChatOut(
            id=c.id,
            userId=c.user_id,
            title=c.title,
            kind=c.kind,
            status=c.status,
            createdAt=c.created_at.isoformat(),
            lastMessageAt=(c.last_message_at or c.created_at).isoformat()
        )
        for c in chats
    ]


@router.post("/chats", response_model=ChatOut)
def create_chat(
    title: str = "New Conversation",
    kind: str = "general",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = Conversation(
        user_id=current_user.id,
        title=title,
        kind=kind,
        status="active",
        last_message_at=datetime.now(timezone.utc),
        is_demo=current_user.is_demo
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    return ChatOut(
        id=conv.id,
        userId=conv.user_id,
        title=conv.title,
        kind=conv.kind,
        status=conv.status,
        createdAt=conv.created_at.isoformat(),
        lastMessageAt=conv.last_message_at.isoformat()
    )


@router.get("/chats/{chat_id}/messages", response_model=List[MessageOut])
def get_chat_messages(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    msgs = db.query(Message).filter(Message.conversation_id == chat_id).order_by(Message.created_at.asc()).all()
    return [
        MessageOut(
            id=m.id,
            chatId=m.conversation_id,
            role=m.role,
            content=m.content,
            contentType=m.content_type,
            createdAt=m.created_at.isoformat(),
            sources=m.sources or [],
            profileCards=m.profile_cards or [],
            applicationDraftId=m.application_draft_id,
            feedback=m.feedback,
            isIncomplete=bool(m.is_incomplete)
        )
        for m in msgs
    ]


@router.post("/chats/{chat_id}/messages", response_model=MessageOut)
def send_chat_message(
    chat_id: str,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    msg = Message(
        conversation_id=chat_id,
        role="user",
        content=payload.content,
        content_type="text",
        is_demo=current_user.is_demo
    )
    db.add(msg)
    conv.last_message_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(msg)

    return MessageOut(
        id=msg.id,
        chatId=msg.conversation_id,
        role=msg.role,
        content=msg.content,
        contentType=msg.content_type,
        createdAt=msg.created_at.isoformat(),
        sources=[],
        profileCards=[],
        feedback=None,
        isIncomplete=False
    )


@router.post("/messages/{message_id}/feedback")
def set_message_feedback(
    message_id: str,
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")

    msg.feedback = payload.rating
    fb = Feedback(
        user_id=current_user.id,
        message_id=message_id,
        rating=payload.rating,
        comment=payload.comment,
        is_demo=current_user.is_demo
    )
    db.add(fb)
    db.commit()
    return {"message": "Feedback recorded."}


@router.get("/notifications", response_model=List[NotificationOut])
def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()

    return [
        NotificationOut(
            id=n.id,
            userId=n.user_id,
            type=n.type,
            title=n.title,
            body=n.body,
            readAt=n.read_at.isoformat() if n.read_at else None,
            createdAt=n.created_at.isoformat(),
            applicationId=n.application_id
        )
        for n in notifs
    ]


@router.put("/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if notif and not notif.read_at:
        notif.read_at = datetime.now(timezone.utc)
        db.commit()
    return {"message": "Marked as read."}


@router.put("/notifications/read-all")
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read_at == None
    ).update({"read_at": datetime.now(timezone.utc)})
    db.commit()
    return {"message": "All notifications marked as read."}
