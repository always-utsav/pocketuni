import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.app.main import app
from backend.app.core.database import SessionLocal, engine
from backend.app.core.security import create_access_token
from backend.app.models.identity import User
from backend.app.models.academic import (
    Laboratory,
    DepartmentProgramme,
    ClassCoordinator,
    ConflictReview,
    BoSMember,
)
from backend.app.models.academic_records import TimetableEntry
from backend.app.models.document import InstitutionalDocument, DocumentChunk
from backend.app.services.timetable_service import timetable_service
from backend.app.services.intent_router import intent_router
from backend.app.services.cai_docx_ingestion import cai_docx_service

client = TestClient(app)


def test_cai_docx_ingestion_and_records():
    """Verify complete ingestion of Centre for AI primary source docx."""
    db = SessionLocal()
    
    # 1. Institutional Document record
    doc = db.query(InstitutionalDocument).filter(
        InstitutionalDocument.file_name == "Centre for Artificial Intelligence data.docx"
    ).first()
    assert doc is not None
    assert doc.status == "PUBLISHED"

    # 2. Conflict review for Applied Mathematics vs Centre for AI
    conflict = db.query(ConflictReview).filter(
        ConflictReview.field_name == "Department Vision and Mission"
    ).first()
    assert conflict is not None
    assert "Applied Mathematics" in conflict.conflict_description
    assert conflict.status == "PENDING"

    # 3. Department Programmes
    progs = db.query(DepartmentProgramme).all()
    assert len(progs) >= 5
    prog_names = [p.name for p in progs]
    assert any("Robotics" in name for name in prog_names)
    assert any("Machine Learning" in name for name in prog_names)
    assert any("Data Science" in name for name in prog_names)

    # 4. Laboratories
    labs = db.query(Laboratory).all()
    assert len(labs) >= 5
    lab_names = [l.name for l in labs]
    assert "Robotics Laboratory" in lab_names
    assert "High Performance Computing (HPC) Laboratory" in lab_names
    assert "Augmented Reality & Virtual Reality (AR/VR) Laboratory" in lab_names

    # 5. Class Coordinators
    coords = db.query(ClassCoordinator).all()
    assert len(coords) >= 10
    air_coord = next((c for c in coords if "Robotics" in c.branch and c.year == "II Year"), None)
    assert air_coord is not None
    assert "Abhishek" in air_coord.faculty_name
    assert air_coord.contact_number == "9045299954"

    # 6. BoS Members
    bos = db.query(BoSMember).all()
    assert len(bos) >= 5

    # 7. Document Chunks indexed for Gemini RAG
    chunks = db.query(DocumentChunk).filter(DocumentChunk.category == "CENTRE_FOR_AI_DOCX").all()
    assert len(chunks) >= 5
    for c in chunks:
        assert c.embedding_json is not None
        assert len(c.embedding_json) > 0

    db.close()


def test_timetable_resolution():
    """Verify student timetable resolver returns exact schedule from master timetable."""
    db = SessionLocal()
    sched = timetable_service.get_student_schedule(
        db=db,
        branch="Information Technology (Artificial Intelligence and Robotics)",
        semester="III Semester",
        section="A",
        day_of_week="Tuesday"
    )
    db.close()

    assert sched["day"] == "Tuesday"
    assert sched["class_count"] >= 4
    assert not sched["is_holiday"]
    # Check periods
    periods = [c["period"] for c in sched["classes"]]
    assert 1 in periods
    assert 2 in periods
    # Period 1 should be Operating Systems in M201
    p1 = next(c for c in sched["classes"] if c["period"] == 1)
    assert "Operating Systems" in p1["subject"]
    assert "M201" in p1["room"]


def test_sunday_holiday_resolution():
    """Verify Sunday resolves as an academic holiday."""
    db = SessionLocal()
    sched = timetable_service.get_student_schedule(
        db=db,
        branch="Information Technology (Artificial Intelligence and Robotics)",
        semester="III Semester",
        day_of_week="Sunday"
    )
    db.close()
    assert sched["day"] == "Sunday"
    assert sched["is_holiday"] is True
    assert sched["class_count"] == 0


def test_faculty_availability_and_disclaimer():
    """Verify faculty availability resolver includes disclaimer with Asia/Kolkata timezone."""
    db = SessionLocal()
    avail = timetable_service.get_faculty_availability(
        db=db,
        target_day="Tuesday",
        time_query="2 PM"
    )
    db.close()

    assert avail["day"] == "Tuesday"
    assert avail["slot"] == 4
    assert avail["timezone"] == "Asia/Kolkata"
    assert "Asia/Kolkata" in avail["disclaimer"]
    assert avail["free_faculty_count"] > 10
    # Busy faculty should be identified
    assert len(avail["busy_faculty"]) >= 1


def test_intent_router_classification():
    """Verify deterministic intent classification for academic inquiries."""
    assert intent_router.classify_intent("What is my timetable tomorrow?") == "TIMETABLE_QUERY"
    assert intent_router.classify_intent("Which classes do I have on Monday?") == "TIMETABLE_QUERY"
    assert intent_router.classify_intent("Which teacher has no scheduled class at 2 PM?") == "FACULTY_AVAILABILITY"
    assert intent_router.classify_intent("Who is free at 3 PM tomorrow?") == "FACULTY_AVAILABILITY"
    assert intent_router.classify_intent("Who is the class coordinator for 2nd year AIR?") == "CLASS_COORDINATOR_LOOKUP"
    assert intent_router.classify_intent("Which laboratories are available in Centre for AI?") == "LABORATORY_LOOKUP"
    assert intent_router.classify_intent("I want to apply for leave for hackathon") == "APPLICATION_WORKFLOW"


def test_avatar_privacy_and_endpoint():
    """Verify voluntary avatar generation endpoint and absence of stock unsplash URLs."""
    db = SessionLocal()
    # 1. Zero unsplash photos in DB
    user_with_unsplash = db.query(User).filter(User.picture_url.ilike("%unsplash%")).first()
    assert user_with_unsplash is None

    # 2. Test avatar generation
    student = db.query(User).filter(User.email == "aarav.sharma@example.invalid").first()
    db.close()
    assert student is not None

    token = create_access_token(subject=student.id, role="STUDENT", email=student.email)
    res = client.post("/api/v1/students/me/avatar", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "avatarUrl" in res.json()
    assert res.json()["status"] == "SUCCESS"


def test_application_outbox_queue():
    """Verify application dispatch outbox queue endpoint."""
    res_login = client.post("/api/v1/auth/dev-login", json={"email": "utsavkumawat05@gmail.com"})
    token = res_login.json()["access_token"]
    res = client.get("/api/v1/applications/outbox/queue", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
