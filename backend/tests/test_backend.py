import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import engine, SessionLocal, check_db_health
from backend.app.core.security import create_access_token
from backend.app.models.identity import User, Role, UserRole
from backend.app.models.student import StudentProfile, ProfileVisibility
from backend.app.models.faculty import FacultyProfile
from backend.app.models.application import Application
from backend.app.models.academic_records import ResultRecord, ResultSubject
from backend.app.models.document import InstitutionalDocument, DocumentAudience
from backend.app.services.extraction_service import extraction_engine
from backend.app.services.audience_service import audience_service
from backend.app.services.classification_service import classification_service

client = TestClient(app)


# 1. Database Connection & Engine Configuration
def test_postgresql_connection_and_version():
    """Verify engine connects to PostgreSQL 18 and database is pocketuni."""
    db_info = check_db_health()
    assert db_info["status"] == "HEALTHY"
    assert db_info["database"] == "pocketuni"
    assert "postgresql+psycopg" in db_info["driver"]
    assert "PostgreSQL 18" in db_info["version"]
    assert "***" in db_info["url"]  # Password must remain hidden


def test_postgresql_persistence():
    """Verify data persistence across transactions in PostgreSQL."""
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "utsavkumawat05@gmail.com").first()
    assert admin is not None
    assert admin.full_name == "Utsav Kumawat"
    db.close()


def test_alembic_migration_tables():
    """Verify all 50 required tables + alembic_version exist in PostgreSQL."""
    with engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")).scalar()
        assert res >= 50
        alembic_rev = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar()
        assert alembic_rev in ["1e5131ff1c7b", "b09aba9ea876", "f45e46a94da4"]


# 2. System Health Endpoint
def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["database"]["database"] == "pocketuni"
    assert "PostgreSQL 18" in data["database"]["version"]


# 3. Authentication & RBAC
def test_unauthenticated_access_rejected():
    res = client.get("/api/v1/students/me")
    assert res.status_code == 401


def test_dev_login_super_admin():
    res = client.post("/api/v1/auth/dev-login", json={"email": "utsavkumawat05@gmail.com"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "SUPER_ADMIN"
    assert data["email"] == "utsavkumawat05@gmail.com"


def test_spoofed_admin_email_rejected():
    """Verify non-allowlisted email cannot obtain SUPER_ADMIN role."""
    # Unregistered email rejected
    res = client.post("/api/v1/auth/dev-login", json={"email": "attacker@example.invalid"})
    assert res.status_code == 404
    # Student email receives STUDENT role only
    res_student = client.post("/api/v1/auth/dev-login", json={"email": "aarav.sharma@example.invalid"})
    assert res_student.status_code == 200
    assert res_student.json()["role"] == "STUDENT"


def test_student_cannot_access_admin_stats():
    res_login = client.post("/api/v1/auth/dev-login", json={"email": "aarav.sharma@example.invalid"})
    token = res_login.json()["access_token"]
    res = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_super_admin_stats_access():
    res_login = client.post("/api/v1/auth/dev-login", json={"email": "utsavkumawat05@gmail.com"})
    token = res_login.json()["access_token"]
    res = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["totalFaculty"] >= 20
    assert data["totalStudents"] >= 4


# 4. Faculty & Mentorship
def test_faculty_directory_mentor_association():
    res_login = client.post("/api/v1/auth/dev-login", json={"email": "aarav.sharma@example.invalid"})
    token = res_login.json()["access_token"]
    res = client.get("/api/v1/faculty/directory", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    faculty = res.json()
    assert len(faculty) >= 20
    # Mentor Dr. Mausam Chouksey must be verified and present
    mentor = next((f for f in faculty if "Mausam" in f["name"]), None)
    assert mentor is not None
    assert mentor["isMentor"] is True
    assert mentor["verificationStatus"] == "VERIFIED_OFFICIAL_SOURCE"


# 5. Strict Results Privacy
def test_strict_result_privacy():
    db = SessionLocal()
    st = db.query(User).filter(User.roll_number.like("DEMO-%")).first()
    db.close()
    assert st is not None
    token = create_access_token(subject=st.id, role="STUDENT", email=st.email)
    res = client.get("/api/v1/results/my-results", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    for r in res.json():
        assert r["rollNumber"] == st.roll_number


# 6. Document Extraction on Supplied Materials
def test_induction_notice_extraction():
    """Verify First Year Induction Notice extraction."""
    fpath = os.path.abspath("data/seed/incoming/Firsty_year_Induction_2025  .docx.pdf")
    if os.path.exists(fpath):
        res = extraction_engine.extract(fpath, "application/pdf")
        assert res.status == "COMPLETED"
        assert res.pages_processed == 6
        assert len(res.contents) > 20
        clf = classification_service.classify_and_extract_metadata(
            "Induction Notice", res.contents, res.tables, "Firsty_year_Induction_2025.pdf"
        )
        assert clf["category"] == "INDUCTION_NOTICE"
        assert clf["batch"] == "2025-26"


def test_scheme_and_syllabus_extraction():
    """Verify II Year Scheme & III Year Syllabus extraction and separation."""
    scheme_path = os.path.abspath("data/seed/incoming/II Year Scheme admitted in session 2025-26.pdf")
    if os.path.exists(scheme_path):
        res_scheme = extraction_engine.extract(scheme_path, "application/pdf")
        assert res_scheme.status == "COMPLETED"
        assert res_scheme.tables_found >= 4
        clf_scheme = classification_service.classify_and_extract_metadata(
            "II Year Scheme", res_scheme.contents, res_scheme.tables, os.path.basename(scheme_path)
        )
        assert clf_scheme["category"] == "SCHEME_OF_STUDY"
        assert clf_scheme["semester"] == "III Semester"


def test_timetable_ocr_extraction():
    """Verify PyMuPDF + Tesseract OCR extraction on scanned timetable."""
    tt_path = os.path.abspath("data/seed/incoming/III Sem TT July-Dec 2026.pdf")
    if os.path.exists(tt_path):
        res = extraction_engine.extract(tt_path, "application/pdf")
        assert res.pages_processed == 4
        assert res.ocr_applied is True
        assert len(res.contents) > 10
        clf = classification_service.classify_and_extract_metadata(
            "III Sem Time Table", res.contents, res.tables, os.path.basename(tt_path)
        )
        assert clf["category"] == "TIMETABLE"
        assert clf["semester"] == "III Semester"


def test_internal_marks_confidentiality_and_reconciliation():
    """Verify internal marks confidential classification, restricted audience, and reconciliation."""
    marks_path = os.path.abspath("data/seed/incoming/2nd semester minor 2 Lab and theory marks.pdf")
    if os.path.exists(marks_path):
        res = extraction_engine.extract(marks_path, "application/pdf")
        assert res.status == "COMPLETED"
        assert res.tables_found >= 10
        clf = classification_service.classify_and_extract_metadata(
            "Minor 2 Marks", res.contents, res.tables, os.path.basename(marks_path)
        )
        assert clf["category"] == "INTERNAL_MARKS"
        assert clf["is_sensitive"] is True
        assert clf["target_roles"] == ["SUPER_ADMIN"]


def test_professional_certifications_extraction():
    """Verify Professional Certification List extraction."""
    cert_path = os.path.abspath("data/seed/incoming/Professional_Certification_Course_List.pdf")
    if os.path.exists(cert_path):
        res = extraction_engine.extract(cert_path, "application/pdf")
        assert res.status == "COMPLETED"
        clf = classification_service.classify_and_extract_metadata(
            "Certification Course List", res.contents, res.tables, os.path.basename(cert_path)
        )
        assert clf["category"] == "PROFESSIONAL_CERTIFICATION_LIST"
        assert len(res.specialized_data.get("professional_certifications", [])) >= 10


# 7. Document Workflow & Audit Trail
def test_document_publishing_and_audit():
    res_login = client.post("/api/v1/auth/dev-login", json={"email": "utsavkumawat05@gmail.com"})
    token = res_login.json()["access_token"]

    # Upload test notice
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test_circular.txt", b"Official Circular: Holiday notice for Diwali 2026.", "text/plain")},
        data={"title": "Official Diwali Circular", "category": "GENERAL_NOTICE"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    # Publish document
    pub_res = client.post(
        f"/api/v1/documents/{doc_id}/publish",
        json={"isAuthoritative": True, "changeSummary": "Published by Super Admin"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "PUBLISHED"

    # Verify audit logs
    audit_res = client.get("/api/v1/audit", headers={"Authorization": f"Bearer {token}"})
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert any(log["action"] == "DOCUMENT_PUBLISH" for log in logs)
