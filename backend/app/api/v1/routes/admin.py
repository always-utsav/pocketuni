import os
import shutil
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db, is_sqlite
from backend.app.core.permissions import require_super_admin, get_current_user
from backend.app.models.identity import User
from backend.app.models.student import StudentProfile
from backend.app.models.faculty import FacultyProfile
from backend.app.models.application import Application
from backend.app.models.document import InstitutionalDocument
from backend.app.models.academic import Department, Programme
from backend.app.models.admin import AuditLog
from backend.app.schemas.admin import AdminStatsOut, SystemHealthOut

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
