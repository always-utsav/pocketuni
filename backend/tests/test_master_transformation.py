import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.core.security import create_access_token
from backend.app.models.identity import User
from backend.app.models.faculty import FacultyProfile as FacultyProfileModel
from backend.app.models.academic_records import TimetableEntry
from backend.app.models.document import InstitutionalDocument
from backend.app.services.timetable_service import timetable_service, SLOT_TIMINGS

client = TestClient(app)


# 1. Three-Account Sandbox Login
def test_sandbox_login_super_admin():
    res = client.post("/api/v1/auth/sandbox-login", json={"role": "SUPER_ADMIN"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "SUPER_ADMIN"
    assert data["user"]["email"] == "utsavkumawat05@gmail.com"


def test_sandbox_login_faculty():
    res = client.post("/api/v1/auth/sandbox-login", json={"role": "FACULTY"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "FACULTY"
    assert "chouksey" in data["user"]["email"].lower()


def test_sandbox_login_student():
    res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "STUDENT"
    assert data["user"]["email"] == "aarav.sharma@example.invalid"


def test_sandbox_login_invalid_role():
    res = client.post("/api/v1/auth/sandbox-login", json={"role": "UNKNOWN_ROLE"})
    assert res.status_code == 400


# 2. Google OAuth GET Callback (405 Prevention)
def test_google_oauth_callback_get_without_params():
    res = client.get("/api/v1/auth/google/callback", follow_redirects=False)
    # Redirects cleanly to frontend with query parameter error, never 405 Method Not Allowed
    assert res.status_code == 307
    assert "error=Missing" in res.headers.get("location", "")


# 3. Application Outbox Queue Security
def test_outbox_queue_unauthenticated():
    res = client.get("/api/v1/applications/outbox/queue")
    assert res.status_code == 401


def test_outbox_queue_forbidden_for_student():
    student_res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    token = student_res.json()["access_token"]
    res = client.get("/api/v1/applications/outbox/queue", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_outbox_queue_forbidden_for_faculty():
    faculty_res = client.post("/api/v1/auth/sandbox-login", json={"role": "FACULTY"})
    token = faculty_res.json()["access_token"]
    res = client.get("/api/v1/applications/outbox/queue", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_outbox_queue_allowed_for_super_admin():
    admin_res = client.post("/api/v1/auth/sandbox-login", json={"role": "SUPER_ADMIN"})
    token = admin_res.json()["access_token"]
    res = client.get("/api/v1/applications/outbox/queue", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# 4. Chat Isolation & Rename
def test_chat_isolation_and_rename():
    student_res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    student_token = student_res.json()["access_token"]

    faculty_res = client.post("/api/v1/auth/sandbox-login", json={"role": "FACULTY"})
    faculty_token = faculty_res.json()["access_token"]

    # Student creates a conversation
    create_res = client.post(
        "/api/v1/chat/conversations",
        json={"title": "Original Title", "kind": "general"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert create_res.status_code == 200
    conv_id = create_res.json()["id"]

    # Student renames their conversation
    patch_res = client.patch(
        f"/api/v1/chat/conversations/{conv_id}/title",
        json={"title": "Renamed Study Session"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Renamed Study Session"

    # Faculty attempts to access Student's conversation -> 404 Not Found (isolated)
    cross_res = client.get(
        f"/api/v1/chat/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    assert cross_res.status_code == 404


# 5. Timetable Exact Timings & No Unsafe Defaults
def test_timetable_period_slots_authoritative():
    """Verify period slot timings match official scanned MITS timetables."""
    slots = SLOT_TIMINGS
    assert slots[1] == ("10:00 AM", "11:00 AM", "Period 1")
    assert slots[2] == ("11:00 AM", "12:00 PM", "Period 2")
    assert slots[3] == ("12:00 PM", "01:00 PM", "Period 3")
    assert slots[4] == ("02:00 PM", "03:00 PM", "Period 4")
    assert slots[5] == ("03:00 PM", "04:00 PM", "Period 5")
    assert slots[6] == ("04:00 PM", "05:00 PM", "Period 6")


def test_timetable_no_unsafe_defaults():
    from backend.app.services.intent_router import intent_router
    db = SessionLocal()
    try:
        # Generic query with no profile context and no branch/sem specified
        res = intent_router.route_query(
            db=db,
            query="What is the timetable tomorrow?",
            user=None
        )
        assert res is not None
        assert res.get("needs_clarification") is True
        assert "specify your branch" in res["answer"].lower()
    finally:
        db.close()


def test_timetable_unsupported_branch_honesty():
    from backend.app.services.intent_router import intent_router
    db = SessionLocal()
    try:
        res = intent_router.route_query(
            db=db,
            query="Show Civil Engineering 5th semester timetable",
            user=None
        )
        assert res is not None
        assert "Centre for Artificial Intelligence programmes" in res["answer"]
    finally:
        db.close()


# 6. Faculty Availability Known Coverage Complement
def test_faculty_availability_known_coverage():
    db = SessionLocal()
    try:
        avail = timetable_service.get_faculty_availability(
            db=db,
            target_day="Monday",
            time_query="10:00"
        )
        assert "busy_faculty" in avail
        assert "free_faculty" in avail
        assert "unknown_coverage_count" in avail
        assert avail["unknown_coverage_count"] >= 1
        for f in avail["free_faculty"]:
            assert "According to the published timetable" in f["status"]
    finally:
        db.close()


# 7. Student Discovery Privacy
def test_student_discovery_excludes_demo_and_private_contacts():
    student_res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    token = student_res.json()["access_token"]

    res = client.get("/api/v1/students/discovery", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    cards = res.json()
    for card in cards:
        # Strict privacy checks:
        assert card["is_demo"] is False
        assert card["studentId"] != student_res.json()["user"]["id"]  # Self excluded


# 8. Avatar Upload Security & Monogram
def test_avatar_svg_monogram():
    student_res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    token = student_res.json()["access_token"]

    res = client.post("/api/v1/students/me/avatar/upload", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "avatarUrl" in data
    assert "monogram" in data["avatarUrl"]


def test_avatar_invalid_extension_rejected():
    student_res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    token = student_res.json()["access_token"]

    fake_file = io.BytesIO(b"alert('xss')")
    res = client.post(
        "/api/v1/students/me/avatar/upload",
        files={"file": ("malicious.exe", fake_file, "application/x-msdownload")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 400


# 9. Faculty Profile Enrichment & Department Filtering
def test_faculty_department_filtering():
    student_res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    token = student_res.json()["access_token"]

    # Filter by CSE
    res_cse = client.get("/api/v1/faculty/directory?department=CSE", headers={"Authorization": f"Bearer {token}"})
    assert res_cse.status_code == 200
    cse_faculty = res_cse.json()
    assert len(cse_faculty) >= 5

    # Filter by IoT
    res_iot = client.get("/api/v1/faculty/directory?department=IoT", headers={"Authorization": f"Bearer {token}"})
    assert res_iot.status_code == 200
    iot_faculty = res_iot.json()
    assert len(iot_faculty) >= 4


def test_three_specified_faculty_enriched():
    db = SessionLocal()
    try:
        dubey = db.query(FacultyProfileModel).join(User).filter(User.full_name.like("%Shradha Dubey%")).first()
        assert dubey is not None
        assert dubey.department == "Computer Science & Engineering"
        assert len(dubey.publications_json or []) >= 5
        assert len(dubey.professional_highlights_json or []) >= 3

        ansari = db.query(FacultyProfileModel).join(User).filter(User.full_name.like("%Aftab Ahmed Ansari%")).first()
        assert ansari is not None
        assert "Internet of Things" in ansari.department
        assert len(ansari.publications_json or []) >= 4

        sharma = db.query(FacultyProfileModel).join(User).filter(User.full_name.like("%Ramnaresh Sharma%")).first()
        assert sharma is not None
        assert sharma.department == "Computer Science & Engineering"
        assert len(sharma.publications_json or []) >= 4
    finally:
        db.close()


# 10. Confidential Document Protection
def test_confidential_document_restricted():
    db = SessionLocal()
    try:
        conf_doc = db.query(InstitutionalDocument).filter(
            InstitutionalDocument.title.like("%marks%")
        ).first()
        if conf_doc:
            assert conf_doc.is_deleted is True or conf_doc.status == "RESTRICTED_CONFIDENTIAL"
            assert conf_doc.is_current_published is False
    finally:
        db.close()
