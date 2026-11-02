from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user, require_student
from backend.app.models.identity import User
from backend.app.models.student import StudentProfile, StudentSkill, Project
from backend.app.schemas.student import (
    StudentProfileUpdate,
    StudentMatchCardSchema,
)
from backend.app.services.audit_service import log_audit_event
from backend.app.services.excel_service import excel_service

router = APIRouter()


@router.get("/me")
def get_my_student_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile record not found.")

    skills_data = [
        {"id": s.id, "name": s.skill_name, "proficiency": s.proficiency, "category": s.category}
        for s in profile.skills
    ]
    projects_data = [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "repoUrl": p.repo_url,
            "liveUrl": p.live_url,
            "techNotes": p.tech_notes or []
        }
        for p in profile.projects
    ]

    return {
        "studentId": current_user.id,
        "fullName": current_user.full_name,
        "email": current_user.email,
        "rollNumber": current_user.roll_number,
        "enrolmentNumber": profile.enrolment_number or current_user.roll_number,
        "department": current_user.department_name or "Centre for Artificial Intelligence",
        "programme": profile.programme or "B.Tech",
        "branch": current_user.branch,
        "specialization": profile.specialization or "",
        "batch": profile.batch or "",
        "semester": profile.semester or 1,
        "section": profile.section or "A",
        "academicYear": profile.academic_year or "2026-2027",
        "dateOfAdmission": profile.date_of_admission or "",
        "yearOfStudy": current_user.year_of_study,
        "bio": profile.bio or "",
        "lookingFor": profile.looking_for or "",
        "openForHackathons": profile.open_for_hackathons,
        "openSourceContributor": profile.open_source_contributor,
        "competitiveProgramming": profile.competitive_programming,
        "competitiveHandles": profile.competitive_handles or {},
        "githubUrl": profile.github_url or "",
        "linkedinUrl": profile.linkedin_url or "",
        "portfolioUrl": profile.portfolio_url or "",
        "resumeUrl": profile.resume_url or "",
        "achievements": profile.achievements or [],
        "certifications": profile.certifications or [],
        "experience": profile.experience or [],
        "availabilityHoursPerWeek": profile.availability_hours_per_week,
        "availabilityNotes": profile.availability_notes or "",
        "preferredRoles": profile.preferred_roles or [],
        "clubs": profile.clubs or [],
        "techStack": profile.tech_stack or [],
        "interests": profile.interests or [],
        "domains": profile.domains or [],
        "skills": skills_data,
        "projects": projects_data,
        "profileVisible": profile.visibility.is_public if profile.visibility else True,
        "completenessScore": profile.completeness_score,
        "dataSource": profile.data_source,
        "is_demo": current_user.is_demo
    }


@router.put("/me")
def update_my_student_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    if payload.bio is not None:
        profile.bio = payload.bio
    if payload.lookingFor is not None:
        profile.looking_for = payload.lookingFor
    if payload.openForHackathons is not None:
        profile.open_for_hackathons = payload.openForHackathons
    if payload.openSourceContributor is not None:
        profile.open_source_contributor = payload.openSourceContributor
    if payload.competitiveProgramming is not None:
        profile.competitive_programming = payload.competitiveProgramming
    if payload.competitiveHandles is not None:
        profile.competitive_handles = payload.competitiveHandles
    if payload.githubUrl is not None:
        profile.github_url = payload.githubUrl
    if payload.linkedinUrl is not None:
        profile.linkedin_url = payload.linkedinUrl
    if payload.portfolioUrl is not None:
        profile.portfolio_url = payload.portfolioUrl
    if payload.availabilityHoursPerWeek is not None:
        profile.availability_hours_per_week = payload.availabilityHoursPerWeek
    if payload.availabilityNotes is not None:
        profile.availability_notes = payload.availabilityNotes
    if payload.preferredRoles is not None:
        profile.preferred_roles = payload.preferredRoles
    if payload.clubs is not None:
        profile.clubs = payload.clubs
    if payload.techStack is not None:
        profile.tech_stack = payload.techStack
    if payload.interests is not None:
        profile.interests = payload.interests
    if payload.domains is not None:
        profile.domains = payload.domains
    if payload.profileVisible is not None and profile.visibility:
        profile.visibility.is_public = payload.profileVisible

    # Update skills if provided
    if payload.skills is not None:
        # Clear existing skills
        db.query(StudentSkill).filter(StudentSkill.student_profile_id == profile.id).delete()
        for sk in payload.skills:
            new_sk = StudentSkill(
                student_profile_id=profile.id,
                skill_name=sk.name,
                proficiency=sk.proficiency,
                category=sk.category
            )
            db.add(new_sk)

    # Update projects if provided
    if payload.projects is not None:
        db.query(Project).filter(Project.student_profile_id == profile.id).delete()
        for pr in payload.projects:
            new_pr = Project(
                student_profile_id=profile.id,
                title=pr.title,
                description=pr.description,
                repo_url=pr.repoUrl,
                live_url=pr.liveUrl,
                tech_notes=pr.techNotes
            )
            db.add(new_pr)

    db.commit()

    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="STUDENT",
        action="UPDATE_STUDENT_PROFILE",
        target_entity="StudentProfile",
        target_id=profile.id,
        change_summary=f"Student updated editable profile fields for {current_user.email}"
    )

    # Sync to Excel workbook mirror
    excel_service.sync_user_profile(db, current_user.id)

    return {"message": "Profile updated successfully."}


@router.get("/discovery", response_model=List[StudentMatchCardSchema])
def discover_students(
    query: Optional[str] = Query(None, description="Search query by skill or interest"),
    branch: Optional[str] = Query(None),
    hackathons_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search and filter public student profiles for peer collaboration and hackathons.
    Does not expose sensitive academic marks or private contact details.
    """
    profiles = db.query(StudentProfile).join(User).filter(
        User.is_deleted == False,
        User.is_active == True
    ).all()

    cards: List[StudentMatchCardSchema] = []
    q_norm = (query or "").lower().strip()

    for p in profiles:
        user = p.user
        if not user or (p.visibility and not p.visibility.is_public):
            continue
        if hackathons_only and not p.open_for_hackathons:
            continue
        if branch and user.branch and branch.lower() not in user.branch.lower():
            continue

        skills = [s.skill_name for s in p.skills]
        all_text = f"{user.full_name} {user.branch} {p.bio} {' '.join(skills)} {' '.join(p.interests or [])} {' '.join(p.preferred_roles or [])}".lower()

        if q_norm and q_norm not in all_text:
            continue

        cards.append(
            StudentMatchCardSchema(
                studentId=user.id,
                name=user.full_name,
                email=user.email,
                pictureUrl=user.picture_url or None,
                branch=user.branch or "Artificial Intelligence",
                year=int(user.year_of_study) if user.year_of_study and str(user.year_of_study).isdigit() else 2,
                rollNumber=user.roll_number,
                bio=p.bio or "",
                matchedTags=[sk for sk in skills if q_norm and q_norm in sk.lower()],
                topSkills=skills[:6],
                openForHackathons=p.open_for_hackathons,
                preferredRoles=p.preferred_roles or [],
                githubUrl=p.github_url,
                linkedinUrl=p.linkedin_url,
                is_demo=user.is_demo
            )
        )

    return cards


@router.post("/me/avatar")
async def upload_student_avatar(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Voluntary avatar upload or initials SVG generation.
    Enforces privacy by not using stock Unsplash faces.
    """
    import os
    from backend.app.core.config import settings

    # Generate personalized institutional SVG avatar
    initials = "".join([part[0] for part in current_user.full_name.split()[:2]]).upper() or "ST"
    svg_avatar = f"""<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
      <rect width="128" height="128" fill="#202C39" rx="64"/>
      <text x="64" y="74" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="44" font-weight="600" fill="#F7F6F2" text-anchor="middle" dominant-baseline="middle">{initials}</text>
    </svg>"""

    avatar_dir = os.path.join(settings.STORAGE_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    fname = f"avatar_{current_user.id}.svg"
    fpath = os.path.join(avatar_dir, fname)

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(svg_avatar)

    avatar_url = f"/api/v1/students/me/avatar/file/{fname}"
    current_user.picture_url = avatar_url
    db.commit()

    return {
        "status": "SUCCESS",
        "avatarUrl": avatar_url,
        "message": "Avatar updated successfully."
    }


@router.get("/me/avatar/file/{filename}")
def serve_avatar_file(filename: str):
    import os
    from fastapi.responses import FileResponse, Response
    from backend.app.core.config import settings

    fpath = os.path.join(settings.STORAGE_DIR, "avatars", filename)
    if not os.path.exists(fpath):
        # Return fallback SVG
        svg = """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect width="128" height="128" fill="#202C39" rx="64"/><text x="64" y="74" font-family="sans-serif" font-size="40" fill="#F7F6F2" text-anchor="middle" dominant-baseline="middle">PU</text></svg>"""
        return Response(content=svg, media_type="image/svg+xml")

    return FileResponse(fpath, media_type="image/svg+xml")
