import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user
from backend.app.models.identity import User
from backend.app.models.communication import Conversation, Message, Feedback
from backend.app.services.rag_service import rag_service
from backend.app.services.gemini_service import gemini_service

router = APIRouter()

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    kind: Optional[str] = "general"

class ConversationUpdate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    content: str

class FeedbackCreate(BaseModel):
    rating: int  # 1 or -1
    comment: Optional[str] = None

@router.post("/conversations")
def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = Conversation(
        user_id=current_user.id,
        title=payload.title or "New Conversation",
        kind=payload.kind or "general",
        status="active",
        last_message_at=datetime.now(timezone.utc)
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {
        "id": conv.id,
        "title": conv.title,
        "kind": conv.kind,
        "status": conv.status,
        "createdAt": conv.created_at.isoformat(),
        "lastMessageAt": conv.last_message_at.isoformat()
    }

@router.get("/conversations")
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_deleted == False
    ).order_by(Conversation.last_message_at.desc()).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "kind": c.kind,
            "status": c.status,
            "createdAt": c.created_at.isoformat(),
            "lastMessageAt": c.last_message_at.isoformat() if c.last_message_at else c.created_at.isoformat()
        }
        for c in convs
    ]

@router.get("/conversations/{conv_id}")
def get_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id,
        Conversation.is_deleted == False
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    msgs = db.query(Message).filter(
        Message.conversation_id == conv.id,
        Message.is_deleted == False
    ).order_by(Message.created_at.asc()).all()

    return {
        "id": conv.id,
        "title": conv.title,
        "kind": conv.kind,
        "status": conv.status,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "contentType": m.content_type,
                "sources": m.sources,
                "profileCards": m.profile_cards,
                "feedback": m.feedback,
                "createdAt": m.created_at.isoformat()
            }
            for m in msgs
        ]
    }

@router.patch("/conversations/{conv_id}")
@router.patch("/conversations/{conv_id}/title")
def update_conversation_title(
    conv_id: str,
    payload: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id,
        Conversation.is_deleted == False
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    
    conv.title = payload.title.strip()
    db.commit()
    return {"id": conv.id, "title": conv.title}

@router.delete("/conversations/{conv_id}")
def delete_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conv.is_deleted = True
    db.commit()
    return {"message": "Conversation deleted."}

@router.post("/conversations/{conv_id}/messages")
def send_message(
    conv_id: str,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id,
        Conversation.is_deleted == False
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # 1. Save user message
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=payload.content,
        content_type="text"
    )
    db.add(user_msg)
    db.flush()

    # 2. Fetch past conversation turns for grounding memory
    past_messages = db.query(Message).filter(
        Message.conversation_id == conv.id,
        Message.is_deleted == False
    ).order_by(Message.created_at.asc()).limit(10).all()
    history = [{"role": m.role, "content": m.content} for m in past_messages]

    # 3. Execute RAG query against verified institutional knowledge
    rag_result = rag_service.query_assistant(
        db=db,
        query=payload.content,
        user=current_user,
        conversation_history=history
    )

    # 4. Save assistant response with real citations
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=rag_result["answer"],
        content_type="text",
        sources=rag_result["citations"]
    )
    db.add(assistant_msg)

    # Update conversation title if first message
    if len(past_messages) <= 2 and conv.title == "New Conversation":
        first_words = payload.content.strip().split()[:5]
        conv.title = " ".join(first_words) + "..."
    conv.last_message_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "userMessage": {
            "id": user_msg.id,
            "role": user_msg.role,
            "content": user_msg.content,
            "createdAt": user_msg.created_at.isoformat()
        },
        "assistantMessage": {
            "id": assistant_msg.id,
            "role": assistant_msg.role,
            "content": assistant_msg.content,
            "sources": assistant_msg.sources,
            "widget": rag_result.get("widget"),
            "createdAt": assistant_msg.created_at.isoformat()
        }
    }

@router.get("/conversations/{conv_id}/stream")
async def stream_message(
    conv_id: str,
    query: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Server-Sent Events (SSE) progressive streaming endpoint with grounding and conversation persistence."""
    from backend.app.services.intent_router import intent_router

    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id,
        Conversation.is_deleted == False
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # 1. Record user message in DB
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=query,
        content_type="text"
    )
    db.add(user_msg)
    db.flush()

    # 2. Check for specialized intent (timetable, faculty availability, official links)
    intent_res = intent_router.route_query(db, query, current_user)

    async def event_generator():
        # Handle specialized deterministic institutional intent first
        if intent_res:
            citations = intent_res.get("citations", [])
            yield f"event: citations\ndata: {json.dumps(citations)}\n\n"
            if intent_res.get("widget"):
                yield f"event: widget\ndata: {json.dumps(intent_res['widget'])}\n\n"

            # Stream the authoritative answer
            full_text = intent_res["answer"]
            # Chunk the response slightly for progressive typing illusion
            words = full_text.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3]) + (" " if i + 3 < len(words) else "")
                yield f"event: delta\ndata: {json.dumps({'text': chunk})}\n\n"

            # Persist assistant message
            assistant_msg = Message(
                conversation_id=conv.id,
                role="assistant",
                content=full_text,
                content_type="text",
                sources=citations
            )
            db.add(assistant_msg)
            conv.last_message_at = datetime.now(timezone.utc)
            db.commit()

            yield f"event: done\ndata: {json.dumps({'status': 'completed', 'messageId': assistant_msg.id})}\n\n"
            return

        # 3. Retrieve sources from institutional knowledge base
        sources = rag_service.search_knowledge(db, query, current_user, limit=4)
        citations = [
            {
                "title": s["title"],
                "category": s["category"],
                "page": s["page_number"],
                "section": s["section"],
                "score": s["score"],
                "snippet": s["text"][:160] + "..."
            }
            for s in sources
        ]

        yield f"event: citations\ndata: {json.dumps(citations)}\n\n"

        context_parts = [f"Source ({s['title']}, Page {s['page_number']}):\n{s['text']}" for s in sources]
        context_text = "\n\n".join(context_parts) if context_parts else "No relevant documents found."
        prompt = (
            f"You are PocketUni, an AI institutional assistant for Madhav Institute of Technology & Science (MITS-DU), Gwalior.\n"
            f"Ground your answer strictly on the institutional context below. Do not speculate.\n\n"
            f"Institutional Context:\n{context_text}\n\n"
            f"Question: {query}\nAnswer:"
        )

        full_content = []
        async for token in gemini_service.generate_stream(prompt):
            full_content.append(token)
            yield f"event: delta\ndata: {json.dumps({'text': token})}\n\n"

        complete_answer = "".join(full_content)
        assistant_msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content=complete_answer,
            content_type="text",
            sources=citations
        )
        db.add(assistant_msg)
        conv.last_message_at = datetime.now(timezone.utc)
        db.commit()

        yield f"event: done\ndata: {json.dumps({'status': 'completed', 'messageId': assistant_msg.id})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/messages/{message_id}/feedback")
def submit_feedback(
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
        message_id=msg.id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(fb)
    db.commit()
    return {"message": "Feedback submitted successfully."}
