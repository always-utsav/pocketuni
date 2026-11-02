import os
import shutil
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db, is_sqlite
from backend.app.core.permissions import require_super_admin, get_current_user

logger = logging.getLogger("pocketuni.admin")
from backend.app.models.identity import User
from backend.app.models.student import StudentProfile, StudentSkill
from backend.app.models.faculty import FacultyProfile, FacultyResearchInterest
from backend.app.models.application import Application
from backend.app.models.document import InstitutionalDocument
from backend.app.models.academic import Department, Programme
from backend.app.models.admin import AuditLog
from backend.app.schemas.admin import AdminStatsOut, SystemHealthOut
from backend.app.services.realtime_service import realtime_manager
from backend.app.services.excel_service import excel_service
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

APPLICATION_TEMPLATES = [
    {
        "id": "tpl-leave",
        "title": "Application for Grant of Leave",
        "type": "leave",
        "notice": "PocketUni Sample Template — Verify institutional format before official submission.",
        "template": """Date: {{DATE}}

To,
The Head of Department,
{{DEPARTMENT_NAME}},
Madhav Institute of Technology & Science (MITS),
Gwalior (M.P.) - 474005

Subject: Application for Grant of Leave — Reg.

Respected Sir/Madam,

I am writing to formally request leave of absence from {{START_DATE}} to {{END_DATE}} due to {{REASON}}.

I have informed my class coordinator and arranged with my peers to cover all missed theory classes and laboratory assignments. The relevant documents/prescriptions are attached herewith for your kind consideration.

I earnestly request you to grant me leave for the specified duration and condone the attendance.

Thanking you.

Yours faithfully,

{{STUDENT_NAME}}
Roll Number: {{ROLL_NUMBER}}
Branch: {{BRANCH}}
Year of Study: {{YEAR_OF_STUDY}}
Semester: {{SEMESTER}}"""
    },
    {
        "id": "tpl-bonafide",
        "title": "Application for Bonafide Certificate",
        "type": "bonafide",
        "notice": "PocketUni Sample Template — Verify institutional format before official submission.",
        "template": """Date: {{DATE}}

To,
The Registrar / Dean Academics,
Madhav Institute of Technology & Science (MITS),
Gwalior (M.P.) - 474005

Subject: Request for Issuance of Bonafide Certificate — Reg.

Respected Sir/Madam,

I am a regular bonafide student of {{PROGRAMME}} in {{BRANCH}} at MITS Gwalior, currently enrolled in the {{SEMESTER}} semester (Academic Year {{ACADEMIC_YEAR}}).

I require an official Bonafide Certificate for the purpose of {{PURPOSE}} (e.g., educational scholarship / education loan / passport verification).

Kindly issue the certificate at your earliest convenience. My academic registration details are stated below.

Thanking you.

Yours faithfully,

{{STUDENT_NAME}}
Roll Number: {{ROLL_NUMBER}}
Branch: {{BRANCH}}
Contact: {{STUDENT_EMAIL}}"""
    },
    {
        "id": "tpl-noc",
        "title": "Application for No Objection Certificate (NOC) for Internship",
        "type": "noc",
        "notice": "PocketUni Sample Template — Verify institutional format before official submission.",
        "template": """Date: {{DATE}}

To,
The Head of Department,
{{DEPARTMENT_NAME}},
Madhav Institute of Technology & Science (MITS), Gwalior

Subject: Request for Issuance of No Objection Certificate (NOC) for Industry Internship — Reg.

Respected Sir/Madam,

I have received an offer for a research/industrial internship at {{ORGANIZATION_NAME}} for the period from {{START_DATE}} to {{END_DATE}}.

To complete my joining formalities, I kindly request the department to grant an official No Objection Certificate. I undertake full responsibility to maintain required academic standing and fulfill all syllabus and examination requirements.

Thanking you.

Yours faithfully,

{{STUDENT_NAME}}
Roll Number: {{ROLL_NUMBER}}
Branch: {{BRANCH}}
Year: {{YEAR_OF_STUDY}}"""
    },
    {
        "id": "tpl-character",
        "title": "Application for Character Certificate",
        "type": "general",
        "notice": "PocketUni Sample Template — Verify institutional format before official submission.",
        "template": """Date: {{DATE}}

To,
The Dean of Student Affairs / Director,
Madhav Institute of Technology & Science, Gwalior (M.P.)

Subject: Application for Issuance of Character / Conduct Certificate — Reg.

Respected Sir/Madam,

I am a regular student of {{PROGRAMME}} ({{BRANCH}}) having Roll Number {{ROLL_NUMBER}}. I have maintained satisfactory conduct and academic discipline during my tenure at the institute.

I request you to kindly issue my Character and Conduct Certificate for higher studies / public employment verification.

Thanking you.

Yours faithfully,

{{STUDENT_NAME}}
Roll Number: {{ROLL_NUMBER}}
Branch: {{BRANCH}}"""
    },
    {
        "id": "tpl-permission",
        "title": "Campus Facility & Lab Permission Request",
        "type": "permission",
        "notice": "PocketUni Sample Template — Verify institutional format before official submission.",
        "template": """Date: {{DATE}}

To,
The Faculty In-Charge / Lab Coordinator,
{{DEPARTMENT_NAME}}, MITS Gwalior

Subject: Request for Permission to Access Lab / Campus Facilities after Hours — Reg.

Respected Sir/Madam,

Our project team is currently developing a project for {{EVENT_NAME_OR_PROJECT}}. We require permission to access the {{LAB_NAME}} facility on {{DATES}} between {{TIMINGS}}.

We assure you that all institute safety norms, equipment guidelines, and lab discipline will be strictly followed.

Thanking you.

Yours faithfully,

{{STUDENT_NAME}}
Team Lead / Student Representative
Roll Number: {{ROLL_NUMBER}}"""
    },
    {
        "id": "tpl-general",
        "title": "General Academic Application to HOD/Dean/Director",
        "type": "general",
        "notice": "PocketUni Sample Template — Verify institutional format before official submission.",
        "template": """Date: {{DATE}}

To,
{{RECIPIENT_DESIGNATION}},
{{DEPARTMENT_NAME}},
Madhav Institute of Technology & Science (MITS), Gwalior (M.P.)

Subject: {{SUBJECT}} — Reg.

Respected Sir/Madam,

I beg to submit that {{BODY_OF_APPLICATION}}.

In light of the above circumstances, I earnestly request your kind intervention and favorable consideration.

Thanking you.

Yours faithfully,

{{STUDENT_NAME}}
Roll Number: {{ROLL_NUMBER}}
Programme: {{PROGRAMME}}
Branch: {{BRANCH}}
Academic Year: {{ACADEMIC_YEAR}}"""
    }
]


@router.get("/stats", response_model=AdminStatsOut)
def get_admin_dashboard_stats(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    total_students = db.query(StudentProfile).count()
    total_faculty = db.query(FacultyProfile).filter(FacultyProfile.is_deleted == False).count()
    total_docs = db.query(InstitutionalDocument).filter(InstitutionalDocument.is_deleted == False).count()
    published_docs = db.query(InstitutionalDocument).filter(
        InstitutionalDocument.status == "PUBLISHED",
        InstitutionalDocument.is_deleted == False
    ).count()
    pending_review = db.query(InstitutionalDocument).filter(
        InstitutionalDocument.status.in_(["NEEDS_REVIEW", "READY_TO_PUBLISH"]),
        InstitutionalDocument.is_deleted == False
    ).count()
    total_apps = db.query(Application).filter(Application.is_deleted == False).count()
    pending_apps = db.query(Application).filter(
        Application.status == "sent",
        Application.is_deleted == False
    ).count()
    total_audits = db.query(AuditLog).count()

    return AdminStatsOut(
        totalStudents=total_students,
        totalFaculty=total_faculty,
        totalDocuments=total_docs,
        publishedDocuments=published_docs,
        pendingReviewDocuments=pending_review,
        totalApplications=total_apps,
        pendingApplications=pending_apps,
        totalAudits=total_audits
    )


@router.get("/health", response_model=SystemHealthOut)
def get_system_health(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    storage_ok = os.path.exists(settings.STORAGE_DIR) and os.access(settings.STORAGE_DIR, os.W_OK)
    ocr_available = shutil.which("tesseract") is not None
    db_type = "SQLite (Local fallback)" if is_sqlite else "PostgreSQL (Connected)"

    return SystemHealthOut(
        status="OPERATIONAL",
        database=db_type,
        storageAccessible=storage_ok,
        ocrAvailable=ocr_available,
        environment=settings.ENVIRONMENT,
        version="1.0.0-module1"
    )


@router.get("/templates")
def get_application_templates(current_user: User = Depends(get_current_user)):
    return APPLICATION_TEMPLATES


@router.get("/departments")
def get_departments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "headOfDepartment": d.head_of_department,
            "overview": d.overview
        }
        for d in depts
    ]


@router.get("/programmes")
def get_programmes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    progs = db.query(Programme).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "degree": p.degree,
            "durationYears": p.duration_years,
            "departmentId": p.department_id
        }
        for p in progs
    ]


@router.get("/ai-status")
def get_ai_status(current_user: User = Depends(require_super_admin)):
    """Returns safe operational status of Gemini AI and embedding models."""
    from backend.app.services.gemini_service import gemini_service
    return gemini_service.get_service_status()


@router.post("/documents/{doc_id}/index")
def index_document_for_rag(
    doc_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint to chunk, embed, and index an institutional document
    into PostgreSQL vector storage for authoritative RAG retrieval.
    """
    from backend.app.services.rag_service import rag_service
    res = rag_service.index_document(db, doc_id)
    return res


@router.post("/diagnostics/rag-test")
def test_rag_retrieval(
    payload: Dict[str, Any],
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Diagnostic endpoint to test hybrid retrieval and citations for any query."""
    from backend.app.services.rag_service import rag_service
    query = payload.get("query", "")
    results = rag_service.search_knowledge(db, query, current_user, limit=5)
    return {
        "query": query,
        "resultsCount": len(results),
        "results": results
    }


class AdminStudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    programme: Optional[str] = None
    academicYear: Optional[str] = None
    bio: Optional[str] = None
    pictureUrl: Optional[str] = None
    topSkills: Optional[List[str]] = None


class AdminFacultyProfileUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    centre: Optional[str] = None
    qualification: Optional[str] = None
    officeLocation: Optional[str] = None
    officeHours: Optional[str] = None
    phoneInternal: Optional[str] = None
    phonePublic: Optional[str] = None
    bio: Optional[str] = None
    photoUrl: Optional[str] = None
    researchAreas: Optional[List[str]] = None
    areasOfExpertise: Optional[List[str]] = None
    professionalHighlights: Optional[List[Dict[str, Any]]] = None


@router.put("/students/{student_id}")
def admin_update_student_profile(
    student_id: str,
    payload: AdminStudentProfileUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint to directly update canonical student profile and user records.
    Persists to PostgreSQL, syncs Excel mirror, logs audit event, and broadcasts live WebSocket event.
    """
    profile = db.query(StudentProfile).filter(
        (StudentProfile.id == student_id) | (StudentProfile.user_id == student_id)
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    user = db.query(User).filter(User.id == profile.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student user record not found.")

    # 1. Update User record
    if payload.name is not None:
        user.full_name = payload.name.strip()
    if payload.branch is not None:
        user.branch = payload.branch.strip()
    if payload.pictureUrl is not None:
        user.picture_url = payload.pictureUrl

    # 2. Update StudentProfile record
    if payload.semester is not None:
        profile.semester = payload.semester
    if payload.section is not None:
        profile.section = payload.section.strip().upper()
    if payload.programme is not None:
        profile.programme = payload.programme.strip()
    if payload.academicYear is not None:
        profile.academic_year = payload.academicYear.strip()
    if payload.bio is not None:
        profile.bio = payload.bio.strip()

    # 3. Update skills if provided
    if payload.topSkills is not None:
        db.query(StudentSkill).filter(StudentSkill.student_profile_id == profile.id).delete()
        for sk_name in payload.topSkills:
            if sk_name.strip():
                db.add(StudentSkill(
                    student_profile_id=profile.id,
                    name=sk_name.strip(),
                    proficiency="Advanced",
                    category="Technical"
                ))

    db.commit()
    db.refresh(profile)
    db.refresh(user)

    # 4. Sync Excel mirror
    try:
        excel_service.sync_user_profile(db, user.id)
    except Exception as e:
        logger.warning(f"Excel sync notice: {e}")

    # 5. Log audit event
    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="ADMIN_UPDATE_STUDENT_PROFILE",
        target_entity="StudentProfile",
        target_id=profile.id,
        change_summary=f"Super Admin updated student profile for {user.email} ({user.full_name})",
        actor_user_id=current_user.id
    )

    # 6. Broadcast real-time WebSocket event
    realtime_manager.broadcast_event(
        event_type="student_profile_updated",
        data={
            "studentId": profile.id,
            "userId": user.id,
            "fullName": user.full_name,
            "branch": user.branch,
            "semester": profile.semester,
            "section": profile.section,
            "bio": profile.bio,
            "pictureUrl": user.picture_url,
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
    )

    return {
        "message": "Student profile updated successfully.",
        "student": {
            "id": profile.id,
            "userId": user.id,
            "fullName": user.full_name,
            "branch": user.branch,
            "semester": profile.semester,
            "section": profile.section,
            "bio": profile.bio,
            "pictureUrl": user.picture_url
        }
    }


@router.put("/faculty/{faculty_id}")
def admin_update_faculty_profile(
    faculty_id: str,
    payload: AdminFacultyProfileUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint to directly update canonical faculty profile and user records.
    Persists to PostgreSQL, syncs Excel mirror, logs audit event, and broadcasts live WebSocket event.
    """
    profile = db.query(FacultyProfile).filter(
        (FacultyProfile.id == faculty_id) | (FacultyProfile.user_id == faculty_id)
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")

    user = db.query(User).filter(User.id == profile.user_id).first() if profile.user_id else None

    # 1. Update FacultyProfile fields
    if payload.name is not None:
        profile.name = payload.name.strip()
        if user:
            user.full_name = payload.name.strip()
    if payload.designation is not None:
        profile.designation = payload.designation.strip()
        if user:
            user.designation = payload.designation.strip()
    if payload.department is not None:
        profile.department = payload.department.strip()
        if user:
            user.department_name = payload.department.strip()
    if payload.centre is not None:
        profile.centre = payload.centre.strip()
    if payload.qualification is not None:
        profile.qualification = payload.qualification.strip()
    if payload.officeLocation is not None:
        profile.office_location = payload.officeLocation.strip()
    if payload.officeHours is not None:
        profile.office_hours = payload.officeHours.strip()
    if payload.phoneInternal is not None:
        profile.phone_internal = payload.phoneInternal.strip()
    if payload.phonePublic is not None:
        profile.phone_public = payload.phonePublic.strip()
    if payload.bio is not None:
        profile.bio = payload.bio.strip()
    if payload.photoUrl is not None:
        profile.photo_url = payload.photoUrl.strip()
        if user:
            user.picture_url = payload.photoUrl.strip()
    if payload.areasOfExpertise is not None:
        profile.areas_of_expertise = payload.areasOfExpertise
    if payload.professionalHighlights is not None:
        profile.professional_highlights_json = payload.professionalHighlights

    # 2. Update research interests if provided
    if payload.researchAreas is not None:
        db.query(FacultyResearchInterest).filter(FacultyResearchInterest.faculty_profile_id == profile.id).delete()
        for area in payload.researchAreas:
            if area.strip():
                db.add(FacultyResearchInterest(
                    faculty_profile_id=profile.id,
                    area=area.strip(),
                    is_demo=profile.is_demo
                ))

    db.commit()
    db.refresh(profile)
    if user:
        db.refresh(user)

    # 3. Sync Excel mirror
    if user:
        try:
            excel_service.sync_user_profile(db, user.id)
        except Exception as e:
            logger.warning(f"Excel sync notice: {e}")

    # 4. Log audit event
    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="ADMIN_UPDATE_FACULTY_PROFILE",
        target_entity="FacultyProfile",
        target_id=profile.id,
        change_summary=f"Super Admin updated faculty profile for {profile.email_public} ({profile.name})",
        actor_user_id=current_user.id
    )

    # 5. Broadcast real-time WebSocket event
    realtime_manager.broadcast_event(
        event_type="faculty_profile_updated",
        data={
            "facultyId": profile.id,
            "userId": user.id if user else None,
            "name": profile.name,
            "designation": profile.designation,
            "department": profile.department,
            "qualification": profile.qualification,
            "officeLocation": profile.office_location,
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
    )

    return {
        "message": "Faculty profile updated successfully.",
        "faculty": {
            "id": profile.id,
            "name": profile.name,
            "designation": profile.designation,
            "department": profile.department,
            "qualification": profile.qualification,
            "officeLocation": profile.office_location,
            "photoUrl": profile.photo_url
        }
    }
