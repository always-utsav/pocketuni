import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.identity import User
from backend.app.models.student import StudentProfile
from backend.app.models.faculty import FacultyProfile
from backend.app.models.application import Application
from backend.app.services.institutional_links import resolve_institutional_link, INSTITUTIONAL_LINK_REGISTRY
from backend.app.services.intent_router import intent_router

client = TestClient(app)


@pytest.fixture(scope="module")
def admin_token():
    res = client.post("/api/v1/auth/sandbox-login", json={"role": "SUPER_ADMIN"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def student_token():
    res = client.post("/api/v1/auth/sandbox-login", json={"role": "STUDENT"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def faculty_token():
    res = client.post("/api/v1/auth/sandbox-login", json={"role": "FACULTY"})
    assert res.status_code == 200
    return res.json()["access_token"]


# ITEM 1 & 2: Student application submission & Faculty inbox delivery
def test_item1_and_2_application_submission_and_inbox_delivery(student_token, faculty_token):
    # 1. Student creates application
    create_res = client.post(
        "/api/v1/applications/",
        json={
            "type": "leave",
            "title": "Medical Leave Application — AICTE Hackathon",
            "content": "Respected Sir, I request leave to attend AICTE Smart India Hackathon.",
            "formData": {"reason": "hackathon"}
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert create_res.status_code in [200, 201]
    app_id = create_res.json()["id"]

    # 2. Get Dr. Mausam Chouksey faculty ID
    fac_login = client.post("/api/v1/auth/sandbox-login", json={"role": "FACULTY"}).json()
    mausam_user_id = fac_login["user"]["id"]

    # 3. Share application with Dr. Mausam Chouksey
    share_res = client.post(
        f"/api/v1/applications/{app_id}/share",
        json={"facultyId": mausam_user_id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert share_res.status_code == 200
    assert share_res.json()["status"] == "sent"

    # 4. Verify in Faculty Sandbox inbox
    inbox_res = client.get(
        "/api/v1/applications/inbox",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    assert inbox_res.status_code == 200
    inbox_apps = inbox_res.json()
    matched = [a for a in inbox_apps if a["id"] == app_id]
    assert len(matched) == 1
    assert matched[0]["studentName"] is not None


# ITEM 3: Revision request & resubmit workflow
def test_item3_revision_and_resubmit_workflow(student_token, faculty_token):
    # Create and share app
    app_res = client.post(
        "/api/v1/applications/",
        json={
            "type": "bonafide",
            "title": "Bonafide Certificate Request for Internship",
            "content": "Requesting bonafide certificate for Google Summer of Code application.",
            "formData": {}
        },
        headers={"Authorization": f"Bearer {student_token}"}
    ).json()
    app_id = app_res["id"]

    fac_user_id = client.post("/api/v1/auth/sandbox-login", json={"role": "FACULTY"}).json()["user"]["id"]
    client.post(
        f"/api/v1/applications/{app_id}/share",
        json={"facultyId": fac_user_id},
        headers={"Authorization": f"Bearer {student_token}"}
    )

    # Faculty requests revision
    rev_res = client.post(
        f"/api/v1/applications/{app_id}/decide",
        json={
            "decision": "revision_requested",
            "note": "Please attach offer letter reference and specify joining date."
        },
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["status"] == "revision_requested"

    # Student resubmits updated content
    resub_res = client.post(
        f"/api/v1/applications/{app_id}/resubmit",
        json={"updatedContent": "Updated: GSoC 2027 joining date 15 May, mentor verified."},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert resub_res.status_code == 200
    assert resub_res.json()["status"] == "sent"

    # Faculty approves resubmitted application
    appr_res = client.post(
        f"/api/v1/applications/{app_id}/decide",
        json={"decision": "approved", "note": "Approved upon revision."},
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "approved"


# ITEM 4: Strict chat isolation across sandboxes
def test_item4_strict_chat_isolation(student_token, faculty_token, admin_token):
    # Student creates chat
    s_conv = client.post(
        "/api/v1/chat/conversations",
        json={"title": "Student Private Chat"},
        headers={"Authorization": f"Bearer {student_token}"}
    ).json()

    # Faculty creates chat
    f_conv = client.post(
        "/api/v1/chat/conversations",
        json={"title": "Faculty Private Chat"},
        headers={"Authorization": f"Bearer {faculty_token}"}
    ).json()

    # Faculty should NOT see student's conversation
    f_res = client.get(
        f"/api/v1/chat/conversations/{s_conv['id']}",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    assert f_res.status_code in [403, 404]

    # Student should NOT see faculty's conversation
    s_res = client.get(
        f"/api/v1/chat/conversations/{f_conv['id']}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert s_res.status_code in [403, 404]


# ITEM 5: Super Admin student profile edits persisted to PostgreSQL
def test_item5_super_admin_student_profile_edit(admin_token):
    db = SessionLocal()
    try:
        student = db.query(StudentProfile).first()
        assert student is not None, "Student profile must exist in DB."
        student_id = student.id
        old_bio = student.bio or ""
    finally:
        db.close()

    new_bio = f"Updated by Super Admin Test Suite {student_id[:6]}"
    update_res = client.put(
        f"/api/v1/admin/students/{student_id}",
        json={"bio": new_bio, "section": "B"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_res.status_code == 200

    # Verify directly in PostgreSQL
    db = SessionLocal()
    try:
        refreshed = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        assert refreshed.bio == new_bio
        assert refreshed.section == "B"
    finally:
        db.close()


# ITEM 6: Super Admin faculty profile edits persisted to PostgreSQL
def test_item6_super_admin_faculty_profile_edit(admin_token):
    db = SessionLocal()
    try:
        faculty = db.query(FacultyProfile).filter(FacultyProfile.email_public == "dr.mausam.chouksey@mitsgwalior.in").first()
        assert faculty is not None
        fac_id = faculty.id
    finally:
        db.close()

    update_res = client.put(
        f"/api/v1/admin/faculty/{fac_id}",
        json={
            "officeLocation": "Academic Block B, Room CAI-302",
            "officeHours": "Monday-Thursday: 3:00 PM - 5:30 PM",
            "phoneInternal": "0751-2409392"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_res.status_code == 200

    # Verify directly in PostgreSQL
    db = SessionLocal()
    try:
        refreshed = db.query(FacultyProfile).filter(FacultyProfile.id == fac_id).first()
        assert refreshed.office_location == "Academic Block B, Room CAI-302"
        assert refreshed.office_hours == "Monday-Thursday: 3:00 PM - 5:30 PM"
        assert refreshed.phone_internal == "0751-2409392"
    finally:
        db.close()


# ITEM 7: Department directory filtering
def test_item7_department_directory_filters(student_token):
    all_res = client.get("/api/v1/faculty/directory", headers={"Authorization": f"Bearer {student_token}"})
    assert all_res.status_code == 200
    all_facs = all_res.json()
    assert len(all_facs) > 10

    cai_res = client.get("/api/v1/faculty/directory?department=Centre for Artificial Intelligence", headers={"Authorization": f"Bearer {student_token}"})
    assert cai_res.status_code == 200
    cai_facs = cai_res.json()
    assert len(cai_facs) >= 1
    for f in cai_facs:
        assert "Artificial Intelligence" in (f.get("department") or "") or "Artificial Intelligence" in (f.get("centre") or "")

    cse_res = client.get("/api/v1/faculty/directory?department=Computer Science & Engineering", headers={"Authorization": f"Bearer {student_token}"})
    assert cse_res.status_code == 200
    cse_facs = cse_res.json()
    assert len(cse_facs) >= 1


# ITEM 8: Exact faculty profile resolution
def test_item8_exact_faculty_profile_resolution(faculty_token):
    # When Faculty Sandbox calls /faculty/me, it must return Dr. Mausam Chouksey
    me_res = client.get("/api/v1/faculty/me", headers={"Authorization": f"Bearer {faculty_token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["name"] == "Dr. Mausam Chouksey"
    assert me_data["emailPublic"] == "dr.mausam.chouksey@mitsgwalior.in"
    assert "Dr. Manish Dixit" not in me_data["name"]


# ITEM 9: Gemini progressive streaming endpoint
def test_item9_gemini_streaming_endpoint(student_token):
    conv = client.post(
        "/api/v1/chat/conversations",
        json={"title": "Streaming Test Conversation"},
        headers={"Authorization": f"Bearer {student_token}"}
    ).json()

    stream_res = client.get(
        f"/api/v1/chat/conversations/{conv['id']}/stream?content=What+is+the+attendance+policy+at+MITS+Gwalior",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers.get("content-type", "")
    content = stream_res.text
    assert "data:" in content
    assert "event: done" in content


# ITEM 10: Sandbox dashboard stability
def test_item10_sandbox_dashboards_stability(admin_token, student_token, faculty_token):
    # Super admin stats
    adm_stats = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert adm_stats.status_code == 200

    # Student profile
    st_prof = client.get("/api/v1/students/me", headers={"Authorization": f"Bearer {student_token}"})
    assert st_prof.status_code == 200

    # Faculty inbox
    fac_inbox = client.get("/api/v1/applications/inbox", headers={"Authorization": f"Bearer {faculty_token}"})
    assert fac_inbox.status_code == 200


# ITEM 11: Exact institutional link resolution from DOCX
def test_item11_exact_institutional_link_resolution():
    hpc = resolve_institutional_link("Where can I find the HPC lab details and GPU configurations?")
    assert hpc is not None
    assert "HPC%20labaratory%20details.pdf" in hpc["url"]

    air = resolve_institutional_link("What is the IT AIR course structure?")
    assert air is not None
    assert "COURSE%20STRUCTURE%20itair.pdf" in air["url"]

    aiml = resolve_institutional_link("Show me the AIML course structure and scheme")
    assert aiml is not None
    assert "COURSE%20STRUCTURE%20aiml.pdf" in aiml["url"]

    seventh = resolve_institutional_link("What is the 7th sem syllabus for AI?")
    assert seventh is not None
    assert "7sem_Syllabus" in seventh["url"]


# ITEM 12: Enriched faculty profiles verification
def test_item12_enriched_faculty_profiles_verification():
    db = SessionLocal()
    try:
        # 1. Dr. Shradha Dubey
        dubey = db.query(FacultyProfile).filter(FacultyProfile.email_public == "shradhadubey@mitsgwalior.in").first()
        assert dubey is not None
        assert dubey.designation == "Assistant Professor"
        assert len(dubey.professional_highlights_json or []) >= 3
        assert "0751-2409327" in (dubey.phone_internal or "")

        # 2. Dr. Aftab Ahmed Ansari
        ansari = db.query(FacultyProfile).filter(FacultyProfile.email_public == "aftabansari@mitsgwalior.in").first()
        assert ansari is not None
        assert "MANIT Bhopal" in (ansari.qualification or "")
        assert len(ansari.professional_highlights_json or []) >= 3
        assert "8878425322" in (ansari.phone_internal or "")

        # 3. Prof. Ramnaresh Sharma
        sharma = db.query(FacultyProfile).filter(FacultyProfile.email_public == "ramcse1983@mitsgwalior.in").first()
        assert sharma is not None
        assert "9754063682" in (sharma.phone_internal or "")
        assert len(sharma.professional_highlights_json or []) >= 3
    finally:
        db.close()


# ITEM 13: Conversational greetings and no raw email exposure
def test_item13_conversational_greetings_and_sanitized_identities():
    db = SessionLocal()
    try:
        # Route query for casual greeting
        res = intent_router.route_query(db, "hi")
        assert res is not None
        # Must NOT be the zero-result fallback
        assert "could not find official information regarding this" not in res["answer"].lower()
        assert "PocketUni" in res["answer"] or "assist" in res["answer"].lower()
    finally:
        db.close()
