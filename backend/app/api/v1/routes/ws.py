import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.core.security import decode_access_token
from backend.app.models.identity import User
from backend.app.services.realtime_service import realtime_manager

logger = logging.getLogger("pocketuni.realtime")
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    Authenticated institutional WebSocket connection endpoint.
    Requires a valid JWT access token passed via query parameter.
    """
    # 1. Cryptographic token verification
    token_payload = decode_access_token(token)
    if not token_payload:
        logger.warning("WebSocket rejected: Invalid or expired token.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = token_payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Database user verification
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False, User.is_active == True).first()
        if not user:
            logger.warning(f"WebSocket rejected: User {user_id} not found or inactive.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        roles = [ur.role.name for ur in user.roles if ur.role]
        primary_role = "STUDENT"
        if "SUPER_ADMIN" in roles:
            primary_role = "SUPER_ADMIN"
        elif "FACULTY" in roles:
            primary_role = "FACULTY"

        user_email = user.email
    finally:
        db.close()

    # 3. Register active socket
    await realtime_manager.connect(websocket, user_id=user_id, user_role=primary_role, user_email=user_email)

    try:
        while True:
            # Keepalive and client message loop
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        realtime_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket connection error for user {user_id}: {e}")
        realtime_manager.disconnect(websocket)
