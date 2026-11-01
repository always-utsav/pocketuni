from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import require_super_admin
from backend.app.models.identity import User
from backend.app.models.admin import AuditLog
from backend.app.schemas.admin import AuditLogOut

router = APIRouter()


@router.get("", response_model=List[AuditLogOut])
@router.get("/logs", response_model=List[AuditLogOut])
def get_audit_logs(
    limit: int = Query(50, le=200),
    action: Optional[str] = Query(None),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        AuditLogOut(
            id=l.id,
            actorEmail=l.actor_email,
            actorRole=l.actor_role,
            action=l.action,
            targetEntity=l.target_entity,
            targetId=l.target_id,
            changeSummary=l.change_summary,
            ipAddress=l.ip_address,
            createdAt=l.created_at.isoformat()
        )
        for l in logs
    ]
