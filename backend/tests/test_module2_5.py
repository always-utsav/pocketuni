import os
import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import engine, SessionLocal
from backend.app.models.identity import User, UserRole, Role
from backend.app.models.admin import AuditLog
from backend.app.models.student import StudentProfile
from backend.app.models.faculty import FacultyProfile
from backend.app.models.website import InstitutionalSource, InstitutionalPortal
from backend.app.models.roster import RosterImportBatch
from backend.app.services.oauth_service import google_oauth_service
from backend.app.services.excel_service import excel_service
from backend.app.services.website_ingestion.crawler import polite_crawler

client = TestClient(app)


def get_admin_headers():
    res = client.post("/api/v1/auth/dev-login", json={"email": "utsavkumawat05@gmail.com"})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_student_headers():
    res = client.post("/api/v1/auth/dev-login", json={"email": "aarav.sharma@example.invalid"})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# 1. Super Admin Allowlist & Multi-Admin Verification
def test_super_admin_allowlist_configuration():
    """Verify both utsavkumawat05@gmail.com and guptamahi0207@gmail.com are configured."""
    assert "utsavkumawat05@gmail.com" in settings.SUPER_ADMIN_ALLOWLIST
    assert "guptamahi0207@gmail.com" in settings.SUPER_ADMIN_ALLOWLIST


# 2. Super Admin Controlled Context Switching & Audit Logging
def test_super_admin_context_switching():
    """Verify Super Admin can switch active view to STUDENT and FACULTY with audit logging."""
    headers = get_admin_headers()
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "utsavkumawat05@gmail.com").first()
    assert admin is not None

    # Context switch to FACULTY
    res = client.post("/api/v1/auth/context-switch", json={"target_context": "FACULTY"}, headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["active_context"] == "FACULTY"
    assert "access_token" in data

    # Verify audit log was recorded
    log = db.query(AuditLog).filter(
        AuditLog.actor_user_id == admin.id,
        AuditLog.action == "CONTEXT_SWITCH"
    ).order_by(AuditLog.created_at.desc()).first()
    assert log is not None
    assert "FACULTY" in log.change_summary

    # Context switch to STUDENT
    res2 = client.post("/api/v1/auth/context-switch", json={"target_context": "STUDENT"}, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["active_context"] == "STUDENT"

    # Context switch back to SUPER_ADMIN
    res3 = client.post("/api/v1/auth/context-switch", json={"target_context": "SUPER_ADMIN"}, headers=headers)
    assert res3.status_code == 200
    assert res3.json()["active_context"] == "SUPER_ADMIN"

    db.close()


def test_non_admin_cannot_switch_context():
    """Verify student or faculty cannot switch context."""
    headers = get_student_headers()

    res = client.post("/api/v1/auth/context-switch", json={"target_context": "SUPER_ADMIN"}, headers=headers)
    assert res.status_code == 403
    assert "Only verified Super Admins are permitted to switch dashboard contexts" in res.text


# 3. Domain & Role Institutional Authorization
def test_oauth_domain_and_role_authorization_logic():
    """Verify student/faculty domain checks and role mismatch rejection."""
    # Case 1: Student domain selecting faculty role -> Must be rejected
    with pytest.raises(ValueError) as exc_info:
        google_oauth_service._authorize_identity("rahul@mitsgwl.ac.in", "FACULTY")
    assert "not authorised to access this role" in str(exc_info.value)

    # Case 2: Faculty domain selecting student role -> Must be rejected
    with pytest.raises(ValueError) as exc_info2:
        google_oauth_service._authorize_identity("prof@mitsgwalior.in", "STUDENT")
    assert "not authorised to access this role" in str(exc_info2.value)

    # Case 3: Personal gmail selecting student or faculty -> Must be rejected
    with pytest.raises(ValueError) as exc_info3:
        google_oauth_service._authorize_identity("random_person@gmail.com", "STUDENT")
    assert "official MITS institutional account" in str(exc_info3.value)

    # Case 4: Allowlisted admin email can access any role
    eff_role, ctx = google_oauth_service._authorize_identity("guptamahi0207@gmail.com", "SUPER_ADMIN")
    assert eff_role == "SUPER_ADMIN"
    assert ctx == "SUPER_ADMIN"


# 4. Excel Workbooks Integrity (pocketuni_students.xlsx & pocketuni_faculty.xlsx)
def test_excel_synthetic_students_integrity():
    """Verify pocketuni_students.xlsx contains exactly 10 synthetic students with correct markers."""
    import openpyxl

    path = "pocketuni_students.xlsx"
    assert os.path.exists(path), f"File {path} must exist in root"

    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    header = rows[0]
    data_rows = rows[1:]

    assert len(data_rows) == 10, f"Expected exactly 10 synthetic student records, found {len(data_rows)}"
    assert "roll_number" in header
    assert "institutional_email" in header
    assert "is_demo" in header
    assert "data_source" in header

    for r in data_rows:
        row_dict = dict(zip(header, r))
        # Roll number must have DEMO- prefix
        assert str(row_dict["roll_number"]).startswith("DEMO-")
        # Email must be in reserved .invalid domain
        assert str(row_dict["institutional_email"]).endswith(".invalid")
        # is_demo must be True
        assert bool(row_dict["is_demo"]) is True
        # data_source must be synthetic_demo
        assert str(row_dict["data_source"]) == "synthetic_demo"


def test_excel_faculty_integrity():
    """Verify pocketuni_faculty.xlsx contains synthetic faculty with correct markers."""
    import openpyxl

    path = "pocketuni_faculty.xlsx"
    assert os.path.exists(path), f"File {path} must exist in root"

    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    data_rows = rows[1:]

    assert len(data_rows) >= 1
    header = rows[0]
    for r in data_rows:
        row_dict = dict(zip(header, r))
        assert str(row_dict["institutional_email"]).endswith(".invalid")
        assert bool(row_dict["is_demo"]) is True


# 5. Roster Management Endpoints
def test_roster_preview_and_export_endpoints():
    """Verify /admin/roster/preview and /admin/roster/export endpoints work for Super Admin."""
    headers = get_admin_headers()

    # Test preview with existing pocketuni_students.xlsx
    with open("pocketuni_students.xlsx", "rb") as f:
        res = client.post(
            "/api/v1/admin/roster/preview",
            files={"file": ("pocketuni_students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"entity_type": "students"},
            headers=headers
        )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["total_rows"] == 10
    assert data["valid_rows"] == 10
    assert data["invalid_rows"] == 0

    # Test export students
    exp_res = client.get("/api/v1/admin/roster/export/students", headers=headers)
    assert exp_res.status_code == 200
    assert "spreadsheetml" in exp_res.headers.get("content-type", "")

    # Test export faculty
    exp_fac_res = client.get("/api/v1/admin/roster/export/faculty", headers=headers)
    assert exp_fac_res.status_code == 200

    # Test sync status
    sync_res = client.get("/api/v1/admin/roster/sync-status", headers=headers)
    assert sync_res.status_code == 200


# 6. Field-Level Profile Permissions & Locking
def test_student_cannot_edit_locked_institutional_fields():
    """Verify student PUT /students/me cannot modify rollNumber or semester, only user fields."""
    headers = get_student_headers()
    db = SessionLocal()
    student = db.query(User).filter(User.email == "aarav.sharma@example.invalid").first()
    student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == student.id).first()
    original_roll = student.roll_number
    original_semester = student_profile.semester

    # Attempt to alter locked rollNumber & semester along with bio
    payload = {
        "rollNumber": "HACKED_ROLL_999",
        "semester": "Semester X",
        "bio": "Updated bio by student self-service",
        "skills": [{"name": "Python", "proficiency": "Advanced"}]
    }

    res = client.put("/api/v1/students/me", json=payload, headers=headers)
    assert res.status_code == 200, res.text

    # Re-query DB to verify locked fields were NOT altered
    db.refresh(student)
    db.refresh(student_profile)
    assert student.roll_number == original_roll, "Security violation: Student altered roll_number!"
    assert student_profile.semester == original_semester, "Security violation: Student altered semester!"
    assert student_profile.bio == "Updated bio by student self-service"

    db.close()


def test_super_admin_can_update_locked_institutional_fields():
    """Verify Super Admin can update locked institutional fields via admin endpoint."""
    headers = get_admin_headers()
    db = SessionLocal()
    student = db.query(User).filter(User.email == "aarav.sharma@example.invalid").first()
    student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == student.id).first()

    new_section = "Section AI-Omega"
    res = client.put(
        f"/api/v1/admin/roster/users/{student.id}/institutional-fields",
        json={"section": new_section},
        headers=headers
    )
    assert res.status_code == 200, res.text

    db.refresh(student_profile)
    assert student_profile.section == new_section

    db.close()


# 7. Web Crawler & Institutional Portals Integration
def test_website_sources_and_portals_endpoints():
    """Verify /website/sources and /website/portals return MITS institutional data."""
    admin_headers = get_admin_headers()
    student_headers = get_student_headers()

    res_sources = client.get("/api/v1/website/sources", headers=admin_headers)
    assert res_sources.status_code == 200, res_sources.text
    sources = res_sources.json()
    assert len(sources) >= 2
    urls = [s["base_url"] for s in sources]
    assert any("web.mitsgwalior.in" in u for u in urls)
    assert any("ams.mitsgwalior.in" in u for u in urls)

    res_portals = client.get("/api/v1/website/portals", headers=student_headers)
    assert res_portals.status_code == 200, res_portals.text
    portals = res_portals.json()
    assert len(portals) >= 5
    urls = [p["officialUrl"] for p in portals]
    assert any("ams.mitsgwalior.in" in u for u in urls)
    assert any("moodle" in u.lower() or "ims" in u.lower() or "mitsgwalior" in u.lower() for u in urls)


def test_crawler_ssrf_safety():
    """Verify crawler rejects non-MITS domains and private/internal IP ranges."""
    # Allowlisted official domains
    assert polite_crawler.is_safe_url("https://web.mitsgwalior.in/about") is True
    assert polite_crawler.is_safe_url("https://ams.mitsgwalior.in/") is True

    # Blocked external domains
    assert polite_crawler.is_safe_url("https://google.com") is False
    assert polite_crawler.is_safe_url("https://malicious-site.org/hack") is False

    # Blocked loopback and private networks
    assert polite_crawler.is_safe_url("http://localhost:8000") is False
    assert polite_crawler.is_safe_url("http://127.0.0.1:5432") is False
    assert polite_crawler.is_safe_url("http://169.254.169.254/latest/meta-data") is False
