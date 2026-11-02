from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user, require_student, require_super_admin
from backend.app.services.realtime_service import realtime_manager
from backend.app.models.identity import User
from backend.app.models.application import (
    Application,
    ApplicationVersionModel,
    ApplicationStatusHistory,
    ApplicationShare,
    ApplicationOutbox,
)
from backend.app.models.communication import Notification
from backend.app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationDecisionRequest,
    ApplicationShareRequest,
    ApplicationOut,
    ApplicationVersionOut,
    ApplicationStatusHistoryOut,
)
from backend.app.services.audit_service import log_audit_event

router = APIRouter()


def _serialize_app(app: Application) -> ApplicationOut:
    versions = [
        ApplicationVersionOut(
            id=v.id,
            versionNo=v.version_no,
            content=v.content,
            createdBy=v.created_by_role,
            createdAt=v.created_at.isoformat()
        )
        for v in app.versions
    ]
    status_history = [
        ApplicationStatusHistoryOut(
            id=h.id,
            fromStatus=h.from_status,
            toStatus=h.to_status,
            actorUserId=h.actor_user_id,
            actorName=h.actor_name,
            note=h.note,
            createdAt=h.created_at.isoformat()
        )
        for h in app.status_history
    ]

    student = app.student
    faculty = app.faculty

    return ApplicationOut(
        id=app.id,
        studentId=app.student_id,
        studentName=student.full_name if student else "Student",
        studentEmail=student.email if student else "",
        studentRollNumber=student.roll_number if student else None,
        studentBranch=student.branch if student else None,
        studentYear=int(student.year_of_study) if student and str(student.year_of_study).isdigit() else 2,
        facultyId=app.faculty_id,
        facultyName=faculty.full_name if faculty else (faculty.designation if faculty else None),
        facultyDepartment=faculty.department_name if faculty else None,
        chatId=app.chat_id,
        title=app.title,
        type=app.type,
        status=app.status,
        currentVersionId=f"v-{app.current_version_no}",
        content=app.content,
        versions=versions,
        statusHistory=status_history,
        createdAt=app.created_at.isoformat(),
        sentAt=app.sent_at.isoformat() if app.sent_at else None,
        decidedAt=app.decided_at.isoformat() if app.decided_at else None,
        decisionNote=app.decision_note,
        is_demo=app.is_demo
    )


class ResubmitApplicationRequest(BaseModel):
    updatedContent: str


@router.get("/", response_model=List[ApplicationOut])
@router.get("/inbox", response_model=List[ApplicationOut])
def list_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_roles = [ur.role.name for ur in current_user.roles if ur.role]

    if "SUPER_ADMIN" in user_roles:
        apps = db.query(Application).filter(Application.is_deleted == False).order_by(Application.created_at.desc()).all()
    elif "FACULTY" in user_roles:
        apps = db.query(Application).filter(
            Application.faculty_id == current_user.id,
            Application.status.in_(["sent", "approved", "rejected", "revision_requested"]),
            Application.is_deleted == False
        ).order_by(Application.created_at.desc()).all()
    else:
        apps = db.query(Application).filter(
            Application.student_id == current_user.id,
            Application.is_deleted == False
        ).order_by(Application.created_at.desc()).all()

    return [_serialize_app(a) for a in apps]


@router.get("/{app_id}", response_model=ApplicationOut)
def get_application_by_id(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id, Application.is_deleted == False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    if "SUPER_ADMIN" not in user_roles and app.student_id != current_user.id and app.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this application.")

    return _serialize_app(app)


@router.post("/", response_model=ApplicationOut)
def create_application(
    payload: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    app = Application(
        student_id=current_user.id,
        faculty_id=payload.facultyId,
        chat_id=payload.chatId,
        title=payload.title,
        type=payload.type,
        status="draft",
        content=payload.content,
        current_version_no=1,
        is_demo=current_user.is_demo
    )
    db.add(app)
    db.flush()

    # Initial version
    v = ApplicationVersionModel(
        application_id=app.id,
        version_no=1,
        content=payload.content,
        created_by_role="student",
        is_demo=current_user.is_demo
    )
    db.add(v)

    # Initial history
    h = ApplicationStatusHistory(
        application_id=app.id,
        from_status="created",
        to_status="draft",
        actor_user_id=current_user.id,
        actor_name=current_user.full_name,
        note="Application drafted.",
        is_demo=current_user.is_demo
    )
    db.add(h)
    db.commit()
    db.refresh(app)

    return _serialize_app(app)


@router.put("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: str,
    payload: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id, Application.is_deleted == False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    if app.student_id != current_user.id:
        user_roles = [ur.role.name for ur in current_user.roles if ur.role]
        if "SUPER_ADMIN" not in user_roles:
            raise HTTPException(status_code=403, detail="Forbidden to edit this application.")

    if payload.content is not None and payload.content != app.content:
        app.content = payload.content
        app.current_version_no += 1
        new_v = ApplicationVersionModel(
            application_id=app.id,
            version_no=app.current_version_no,
            content=payload.content,
            created_by_role="student",
            is_demo=app.is_demo
        )
        db.add(new_v)

    if payload.title is not None:
        app.title = payload.title

    db.commit()
    db.refresh(app)
    return _serialize_app(app)


@router.post("/{app_id}/resubmit", response_model=ApplicationOut)
def resubmit_application(
    app_id: str,
    payload: ResubmitApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id, Application.is_deleted == False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    if app.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden to resubmit this application.")

    app.content = payload.updatedContent
    app.status = "sent"
    app.current_version_no += 1
    new_v = ApplicationVersionModel(
        application_id=app.id,
        version_no=app.current_version_no,
        content=payload.updatedContent,
        created_by_role="student",
        is_demo=app.is_demo
    )
    db.add(new_v)

    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status="revision_requested",
        to_status="sent",
        actor_user_id=current_user.id,
        actor_name=current_user.full_name,
        note="Application revised and resubmitted by student.",
        is_demo=app.is_demo
    )
    db.add(hist)
    db.commit()
    db.refresh(app)

    realtime_manager.broadcast_event(
        event_type="application_status_changed",
        data={
            "applicationId": app.id,
            "status": "sent",
            "studentName": current_user.full_name,
            "facultyId": app.faculty_id
        }
    )
    return _serialize_app(app)


@router.post("/{app_id}/share", response_model=ApplicationOut)
def share_application(
    app_id: str,
    payload: ApplicationShareRequest,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id, Application.student_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    faculty = db.query(User).filter(User.id == payload.facultyId).first()
    if not faculty:
        fac_prof = db.query(FacultyProfile).filter(
            (FacultyProfile.id == payload.facultyId) | (FacultyProfile.user_id == payload.facultyId) | (FacultyProfile.email_public == payload.facultyId)
        ).first()
        if fac_prof and fac_prof.user_id:
            faculty = db.query(User).filter(User.id == fac_prof.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Target faculty member not found.")

    prev_status = app.status
    app.status = "sent"
    app.faculty_id = faculty.id
    app.sent_at = datetime.now(timezone.utc)

    # Add history
    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status=prev_status,
        to_status="sent",
        actor_user_id=current_user.id,
        actor_name=current_user.full_name,
        note=payload.note or f"Submitted to {faculty.full_name}",
        is_demo=app.is_demo
    )
    db.add(hist)

    # Create notification for faculty
    notif = Notification(
        user_id=faculty.id,
        type="application_received",
        title="New Application Received",
        body=f"{current_user.full_name} submitted '{app.title}' for your review.",
        application_id=app.id,
        is_demo=app.is_demo
    )
    db.add(notif)

    # Enqueue to institutional outbox (internal delivery is complete, external dispatch is queued)
    outbox = ApplicationOutbox(
        application_id=app.id,
        recipient_email=faculty.email,
        recipient_name=faculty.full_name,
        subject=f"[MITS PocketUni] Student Application: {app.title}",
        body=app.content,
        status="QUEUED",
        provider_response="Queued for external dispatch. Internal delivery completed to Faculty Sandbox Inbox.",
        attempt_count=0,
        dispatched_at=None,
        is_demo=app.is_demo
    )
    db.add(outbox)
    db.commit()
    db.refresh(app)

    # Broadcast real-time event to faculty and super admin
    realtime_manager.broadcast_event(
        event_type="application_received",
        data={
            "applicationId": app.id,
            "title": app.title,
            "studentName": current_user.full_name,
            "facultyId": faculty.id,
            "submittedAt": app.sent_at.isoformat() if app.sent_at else None
        },
        target_user_ids=[faculty.id]
    )
    realtime_manager.broadcast_event(
        event_type="application_status_changed",
        data={"applicationId": app.id, "status": "sent"}
    )

    return _serialize_app(app)


@router.post("/{app_id}/decide", response_model=ApplicationOut)
def decide_application(
    app_id: str,
    payload: ApplicationDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id, Application.is_deleted == False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    if "SUPER_ADMIN" not in user_roles and app.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only assigned faculty or Super Admin can make decisions.")

    decision_status = payload.decision.lower().strip()
    valid_decisions = ["approved", "rejected", "revision_requested"]
    if decision_status not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Decision must be one of: {', '.join(valid_decisions)}"
        )

    prev_status = app.status
    app.status = decision_status
    app.decided_at = datetime.now(timezone.utc)
    app.decision_note = payload.note

    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status=prev_status,
        to_status=decision_status,
        actor_user_id=current_user.id,
        actor_name=current_user.full_name,
        note=payload.note,
        is_demo=app.is_demo
    )
    db.add(hist)

    # Notify student
    if decision_status == "approved":
        notif_type = "application_approved"
        title_msg = "Application Approved"
        body_msg = f"Your application '{app.title}' was approved by {current_user.full_name}."
    elif decision_status == "rejected":
        notif_type = "application_rejected"
        title_msg = "Application Rejected"
        body_msg = f"Your application '{app.title}' was rejected by {current_user.full_name}."
    else:
        notif_type = "application_revision_requested"
        title_msg = "Revision Requested"
        body_msg = f"{current_user.full_name} requested corrections on '{app.title}': {payload.note or 'Please review feedback.'}"

    notif = Notification(
        user_id=app.student_id,
        type=notif_type,
        title=title_msg,
        body=body_msg,
        application_id=app.id,
        is_demo=app.is_demo
    )
    db.add(notif)
    db.commit()
    db.refresh(app)

    # Realtime notification to student
    realtime_manager.broadcast_event(
        event_type="application_decision_made",
        data={
            "applicationId": app.id,
            "status": decision_status,
            "decisionNote": payload.note,
            "facultyName": current_user.full_name,
            "studentId": app.student_id
        },
        target_user_ids=[app.student_id]
    )
    realtime_manager.broadcast_event(
        event_type="application_status_changed",
        data={"applicationId": app.id, "status": decision_status}
    )

    return _serialize_app(app)


@router.delete("/{app_id}")
def delete_application(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    if "SUPER_ADMIN" not in user_roles and app.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    app.is_deleted = True
    db.commit()
    return {"message": "Application deleted."}


class AgentChatRequest(BaseModel):
    message: str
    conversationHistory: Optional[List[Dict[str, str]]] = []
    currentSlots: Optional[Dict[str, Any]] = None


@router.post("/agent-chat")
def application_agent_chat(
    payload: AgentChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Conversational Application Agent:
    Extracts missing application parameters, prompts the student,
    and synthesizes a formal application once all details are known.
    """
    from backend.app.services.application_agent_service import application_agent_service
    res = application_agent_service.process_message(
        db=db,
        student_user=current_user,
        user_message=payload.message,
        conversation_history=payload.conversationHistory or [],
        current_slots=payload.currentSlots or {}
    )
    return res


@router.get("/{app_id}/docx")
def download_application_docx(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import os
    from fastapi.responses import FileResponse
    from backend.app.core.config import settings

    app = db.query(Application).filter(Application.id == app_id, Application.is_deleted == False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    file_path = os.path.join(settings.STORAGE_DIR, "application_documents", f"{app.id}.docx")
    if not os.path.exists(file_path):
        from backend.app.services.application_agent_service import application_agent_service
        file_path = application_agent_service.generate_docx(app.id, app.content, app.title)

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{app.title.replace(' ', '_')}.docx"
    )


@router.get("/outbox/queue")
def list_application_outbox(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Returns the application dispatch outbox queue.
    """
    entries = db.query(ApplicationOutbox).order_by(ApplicationOutbox.created_at.desc()).limit(50).all()
    return [
        {
            "id": e.id,
            "applicationId": e.application_id,
            "recipientEmail": e.recipient_email,
            "recipientName": e.recipient_name,
            "subject": e.subject,
            "status": e.status,
            "providerResponse": e.provider_response,
            "attemptCount": e.attempt_count,
            "dispatchedAt": e.dispatched_at.isoformat() if e.dispatched_at else None,
            "createdAt": e.created_at.isoformat(),
        }
        for e in entries
    ]
