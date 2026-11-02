import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.identity import User
from backend.app.models.faculty import FacultyProfile
from backend.app.services.intent_router import intent_router

client = TestClient(app)


def test_greeting_intent_does_not_trigger_zero_result_fallback():
    """Validates that conversational greetings do not fall back to RAG zero-result apology."""
    db = SessionLocal()
    try:
        for greeting in ["hi", "hello", "hey", "good morning", "who are you", "what can you do"]:
            classified = intent_router.classify_intent(greeting)
            assert classified == "GREETING", f"Failed for query '{greeting}', got {classified}"
            
            res = intent_router.route_query(db, greeting)
            assert res is not None
            assert res["intent"] == "GREETING"
            assert "PocketUni" in res["answer"]
            assert "I could not find official information" not in res["answer"]
            assert len(res["citations"]) > 0
    finally:
        db.close()


def test_faculty_profile_identity_no_mismatch():
    """Validates that faculty sandbox login and /faculty/me return Dr. Mausam Chouksey strictly."""
    res = client.post("/api/v1/auth/sandbox-login?persona=FACULTY")
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_res = client.get("/api/v1/faculty/me", headers=headers)
    assert me_res.status_code == 200, me_res.text
    me_data = me_res.json()
    
    assert me_data["name"] == "Dr. Mausam Chouksey"
    assert "manish dixit" not in me_data["name"].lower()
    assert me_data["department"] == "Centre for Artificial Intelligence"
    assert me_data["emailPublic"] == "dr.mausam.chouksey@mitsgwalior.in"


def test_priority_faculty_profile_enrichment():
    """Validates verified data for Prof. Ramnaresh Sharma, Dr. Shradha Dubey, and Dr. Aftab Ahmed Ansari."""
    db = SessionLocal()
    try:
        # 1. Prof. Ramnaresh Sharma
        sharma = db.query(FacultyProfile).filter(FacultyProfile.email_public == "ramcse1983@mitsgwalior.in").first()
        assert sharma is not None
        assert sharma.name == "Prof. Ramnaresh Sharma"
        assert sharma.phone_internal == "9754063682"
        assert sharma.department == "Computer Science & Engineering"
        assert "kiran" not in sharma.name.lower()
        assert len(sharma.publications_json or []) >= 3
        assert len(sharma.professional_highlights_json or []) >= 3

        # 2. Dr. Shradha Dubey
        dubey = db.query(FacultyProfile).filter(FacultyProfile.email_public == "shradhadubey@mitsgwalior.in").first()
        assert dubey is not None
        assert dubey.name == "Dr. Shradha Dubey"
        assert dubey.phone_internal == "0751-2409327"
        assert "AICTE-NDF" in dubey.qualification
        assert len(dubey.publications_json or []) >= 4
        assert len(dubey.professional_highlights_json or []) >= 4

        # 3. Dr. Aftab Ahmed Ansari
        ansari = db.query(FacultyProfile).filter(FacultyProfile.email_public == "aftabansari@mitsgwalior.in").first()
        assert ansari is not None
        assert ansari.name == "Dr. Aftab Ahmed Ansari"
        assert "Internet of Things" in ansari.department
        assert len(ansari.publications_json or []) >= 3
        assert len(ansari.professional_highlights_json or []) >= 3
    finally:
        db.close()


def test_application_workflow_recipient_resolution():
    """Validates student application creation and sharing to faculty recipient."""
    # 1. Student login
    std_res = client.post("/api/v1/auth/sandbox-login?persona=STUDENT")
    assert std_res.status_code == 200
    std_token = std_res.json()["access_token"]
    std_headers = {"Authorization": f"Bearer {std_token}"}

    # 2. Faculty login
    fac_res = client.post("/api/v1/auth/sandbox-login?persona=FACULTY")
    assert fac_res.status_code == 200
    fac_user_id = fac_res.json()["user"]["id"]

    # 3. Create application
    create_res = client.post("/api/v1/applications/", json={
        "title": "Leave Permission for AI Hackathon",
        "type": "leave",
        "content": "Formal request for attendance dispensation to participate in AI Hackathon."
    }, headers=std_headers)
    assert create_res.status_code == 200
    app_id = create_res.json()["id"]

    # 4. Share to Dr. Mausam Chouksey
    share_res = client.post(f"/api/v1/applications/{app_id}/share", json={
        "facultyId": fac_user_id,
        "note": "Submitted for mentor approval"
    }, headers=std_headers)
    assert share_res.status_code == 200
    shared_data = share_res.json()
    assert shared_data["status"] == "sent"
    assert shared_data["facultyId"] == fac_user_id
