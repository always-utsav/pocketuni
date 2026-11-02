import asyncio
import json
import logging
from typing import Dict, Set, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("pocketuni.realtime")


class RealtimeConnectionManager:
    """
    Manages authenticated WebSocket connections, broadcasting institutional events
    and delivering private events to authorized users in real time.
    """

    def __init__(self):
        # Map of user_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of websocket -> user_metadata (role, email)
        self.connection_meta: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, user_role: str, user_email: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        self.connection_meta[websocket] = {
            "user_id": user_id,
            "role": user_role,
            "email": user_email
        }
        logger.info(f"WebSocket client connected: user={user_id} role={user_role}")

        # Send connection confirmation ACK
        await websocket.send_json({
            "type": "connection_ack",
            "status": "connected",
            "userId": user_id,
            "role": user_role
        })

    def disconnect(self, websocket: WebSocket):
        meta = self.connection_meta.pop(websocket, None)
        if meta:
            user_id = meta.get("user_id")
            if user_id and user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            logger.info(f"WebSocket client disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Dispatches an event directly to all active sockets of a specific user."""
        sockets = list(self.active_connections.get(user_id, set()))
        if not sockets:
            return

        payload = {"type": event_type, "data": data}
        dead_sockets = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception as e:
                logger.warning(f"Failed to send to user {user_id}: {e}")
                dead_sockets.append(ws)

        for ws in dead_sockets:
            self.disconnect(ws)

    async def broadcast(
        self,
        event_type: str,
        data: Dict[str, Any],
        target_user_ids: Optional[List[str]] = None,
        target_roles: Optional[List[str]] = None
    ):
        """
        Broadcasts an event to target users or roles, or to all active clients.
        """
        payload = {"type": event_type, "data": data}
        dead_sockets = []

        for ws, meta in list(self.connection_meta.items()):
            uid = meta.get("user_id")
            role = meta.get("role")

            if target_user_ids and uid not in target_user_ids:
                continue
            if target_roles and role not in target_roles:
                continue

            try:
                await ws.send_json(payload)
            except Exception as e:
                logger.warning(f"Error broadcasting to socket {uid}: {e}")
                dead_sockets.append(ws)

        for ws in dead_sockets:
            self.disconnect(ws)

    def broadcast_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        target_user_ids: Optional[List[str]] = None,
        target_roles: Optional[List[str]] = None
    ):
        """
        Thread-safe synchronous wrapper to dispatch events from standard FastAPI endpoints.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast(event_type, data, target_user_ids, target_roles))
        except RuntimeError:
            # Fallback if called outside active event loop
            try:
                asyncio.run(self.broadcast(event_type, data, target_user_ids, target_roles))
            except Exception as ex:
                logger.warning(f"Could not dispatch realtime event {event_type}: {ex}")


realtime_manager = RealtimeConnectionManager()
