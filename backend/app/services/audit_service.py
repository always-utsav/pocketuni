from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.admin import AuditLog


def log_audit_event(
    db: Session,
    actor_email: str,
    actor_role: str,
    action: str,
    target_entity: str,
    target_id: Optional[str] = None,
    change_summary: str = "",
    actor_user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None
) -> AuditLog:
    log_entry = AuditLog(
        actor_user_id=actor_user_id,
        actor_email=actor_email,
        actor_role=actor_role,
        action=action,
        target_entity=target_entity,
        target_id=target_id,
        change_summary=change_summary,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_context=extra_context or {}
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
