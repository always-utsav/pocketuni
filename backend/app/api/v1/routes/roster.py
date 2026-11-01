import os
import shutil
import tempfile
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_super_admin
from backend.app.models.identity import User
from backend.app.models.student import StudentProfile
from backend.app.models.faculty import FacultyProfile
from backend.app.models.roster import RosterImportBatch, ExcelSyncJob
from backend.app.services.excel_service import excel_service
from backend.app.services.audit_service import log_audit_event

router = APIRouter()


class InstitutionalFieldsUpdateRequest(BaseModel):
    # Student fields
    roll_number: Optional[str] = None
    enrolment_number: Optional[str] = None
    department_name: Optional[str] = None
    programme: Optional[str] = None
    branch: Optional[str] = None
    specialization: Optional[str] = None
    batch: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    academic_year: Optional[str] = None
    date_of_admission: Optional[str] = None

    # Faculty fields
    faculty_identifier: Optional[str] = None
    designation: Optional[str] = None
    centre: Optional[str] = None
    qualification: Optional[str] = None
    official_profile_url: Optional[str] = None


class AccountStatusUpdateRequest(BaseModel):
    is_active: bool


def normalize_entity_type(entity_type: str) -> str:
    cleaned = entity_type.upper().strip()
    if "STUDENT" in cleaned:
        return "STUDENT"
    if "FACULT" in cleaned:
        return "FACULTY"
    return cleaned


@router.post("/preview")
async def preview_roster_file(
    file: UploadFile = File(...),
    entity_type: str = Form(...),
    current_admin: User = Depends(require_super_admin)
):
    """Previews and validates an uploaded student or faculty Excel workbook."""
    entity_type_upper = normalize_entity_type(entity_type)
    if entity_type_upper not in ["STUDENT", "FACULTY"]:
        raise HTTPException(status_code=400, detail="entity_type must be either STUDENT or FACULTY.")

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel (.xlsx, .xls) files are supported.")

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"preview_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        preview = excel_service.preview_workbook(temp_path, entity_type_upper)
        return preview
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/import")
async def import_roster_file(
    file: UploadFile = File(...),
    entity_type: str = Form(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Transactionally imports validated Excel records into PostgreSQL 18."""
    entity_type_upper = normalize_entity_type(entity_type)
    if entity_type_upper not in ["STUDENT", "FACULTY"]:
        raise HTTPException(status_code=400, detail="entity_type must be either STUDENT or FACULTY.")

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"import_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = excel_service.import_workbook(
            db=db,
            file_path=temp_path,
            entity_type=entity_type_upper,
            imported_by_user_id=current_admin.id
        )

        log_audit_event(
            db=db,
            actor_email=current_admin.email,
            actor_role="SUPER_ADMIN",
            action="ROSTER_IMPORT",
            target_entity="RosterImportBatch",
            target_id=str(result.get("batch_id")),
            change_summary=f"Imported {result.get('created', 0)} new and updated {result.get('updated', 0)} {entity_type_upper} records."
        )

        # Trigger mirrored export to keep local workbooks up to date
        excel_service.export_workbook(db, entity_type_upper)

        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/export/{entity_type}")
def export_roster(
    entity_type: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Exports current PostgreSQL student or faculty records into an official Excel file."""
    entity_type_upper = normalize_entity_type(entity_type)
    if entity_type_upper not in ["STUDENT", "FACULTY"]:
        raise HTTPException(status_code=400, detail="entity_type must be either STUDENT or FACULTY.")

    file_path = excel_service.export_workbook(db, entity_type_upper)
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/sync-status")
def get_sync_status(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Returns import batch history and Excel synchronization jobs."""
    batches = db.query(RosterImportBatch).order_by(RosterImportBatch.created_at.desc()).limit(20).all()
    sync_jobs = db.query(ExcelSyncJob).order_by(ExcelSyncJob.created_at.desc()).limit(20).all()

    return {
        "recent_batches": [
            {
                "id": b.id,
                "entity_type": b.entity_type,
                "file_name": b.file_name,
                "status": b.status,
                "total_records": b.total_records,
                "successful_records": b.successful_records,
                "failed_records": b.failed_records,
                "created_at": b.created_at.isoformat() if b.created_at else None
            }
            for b in batches
        ],
        "recent_sync_jobs": [
            {
                "id": j.id,
                "entity_type": j.entity_type,
                "user_email": j.user_email,
                "status": j.status,
                "retry_count": j.retry_count,
                "last_error": j.last_error,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None
            }
            for j in sync_jobs
        ]
    }


@router.put("/users/{user_id}/institutional-fields")
def update_user_institutional_fields(
    user_id: str,
    payload: InstitutionalFieldsUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Allows Super Admin exclusively to edit institution-controlled read-only fields."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    roles = [ur.role.name for ur in user.roles if ur.role]

    if "STUDENT" in roles:
        if payload.roll_number:
            user.roll_number = payload.roll_number
        if payload.department_name:
            user.department_name = payload.department_name
        if payload.branch:
            user.branch = payload.branch

        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if profile:
            if payload.enrolment_number:
                profile.enrolment_number = payload.enrolment_number
            if payload.programme:
                profile.programme = payload.programme
            if payload.specialization:
                profile.specialization = payload.specialization
            if payload.batch:
                profile.batch = payload.batch
            if payload.semester is not None:
                profile.semester = payload.semester
            if payload.section:
                profile.section = payload.section
            if payload.academic_year:
                profile.academic_year = payload.academic_year
            if payload.date_of_admission:
                profile.date_of_admission = payload.date_of_admission

    elif "FACULTY" in roles:
        if payload.designation:
            user.designation = payload.designation
        if payload.department_name:
            user.department_name = payload.department_name

        fac_profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
        if fac_profile:
            if payload.faculty_identifier:
                fac_profile.faculty_identifier = payload.faculty_identifier
            if payload.designation:
                fac_profile.designation = payload.designation
            if payload.department_name:
                fac_profile.department = payload.department_name
            if payload.centre:
                fac_profile.centre = payload.centre
            if payload.qualification:
                fac_profile.qualification = payload.qualification
            if payload.official_profile_url:
                fac_profile.official_profile_url = payload.official_profile_url

    db.commit()

    log_audit_event(
        db=db,
        actor_email=current_admin.email,
        actor_role="SUPER_ADMIN",
        action="UPDATE_INSTITUTIONAL_FIELDS",
        target_entity="User",
        target_id=user.id,
        change_summary=f"Super Admin updated locked institutional fields for {user.email}"
    )

    # Queue Excel sync
    excel_service.sync_user_profile(db, user.id)

    return {"message": "Institutional fields updated successfully."}


@router.post("/users/{user_id}/status")
def toggle_account_status(
    user_id: str,
    payload: AccountStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Enables Super Admin to activate or deactivate user accounts."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = payload.is_active
    db.commit()

    action_label = "ACTIVATED" if payload.is_active else "DEACTIVATED"
    log_audit_event(
        db=db,
        actor_email=current_admin.email,
        actor_role="SUPER_ADMIN",
        action=f"ACCOUNT_{action_label}",
        target_entity="User",
        target_id=user.id,
        change_summary=f"Super Admin {action_label.lower()} account for {user.email}"
    )

    return {"message": f"Account {action_label.lower()} successfully.", "is_active": user.is_active}
