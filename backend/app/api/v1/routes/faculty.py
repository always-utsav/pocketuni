from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user, require_faculty
from backend.app.models.identity import User
from backend.app.models.faculty import FacultyProfile, FacultyPublication, FacultyResearchInterest
from backend.app.schemas.faculty import (
    FacultyProfileOut,
    FacultyProfileUpdateRequest,
    FacultyPublicationSchema,
)
from backend.app.services.audit_service import log_audit_event
from backend.app.services.excel_service import excel_service
from backend.app.services.realtime_service import realtime_manager

router = APIRouter()


def _serialize_faculty(f: FacultyProfile, viewer: User) -> FacultyProfileOut:
    user_roles = [ur.role.name for ur in viewer.roles if ur.role]
    is_privileged = ("SUPER_ADMIN" in user_roles) or (f.user_id == viewer.id)

    # Compile publications from JSON or relational rows
    pubs: List[Dict[str, Any]] = []
    if f.publications_json and isinstance(f.publications_json, list):
        pubs = list(f.publications_json)
    elif f.publications:
        pubs = [
            {
                "title": p.title,
                "journal": p.journal,
                "year": p.year,
                "doi": p.doi
            }
            for p in f.publications
        ]

    areas = [r.area for r in f.research_interests]
    highlights = f.professional_highlights_json if isinstance(f.professional_highlights_json, list) else []
    ext_links = f.external_links_json if isinstance(f.external_links_json, dict) else {}

    return FacultyProfileOut(
        facultyId=f.id,
        name=f.name,
        designation=f.designation,
        department=f.department,
        centre=f.centre,
        qualification=f.qualification,
        researchAreas=areas,
        areasOfExpertise=f.areas_of_expertise or [],
        publications=pubs,
        professionalHighlights=highlights,
        externalLinks=ext_links,
        emailPublic=f.email_public,
        phonePublic=f.phone_public,
        phoneInternal=f.phone_internal if is_privileged else None,
        officeLocation=f.office_location,
        officeHours=f.office_hours,
        photoUrl=f.photo_url,
        bio=f.bio,
        sourceUrl=f.source_url,
        officialProfileUrl=f.official_profile_url,
        verificationStatus=f.verification_status,
        isMentor=f.is_mentor,
        is_demo=f.is_demo
    )


@router.get("/me", response_model=FacultyProfileOut)
def get_my_faculty_profile(
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    f = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
    if not f:
        f = db.query(FacultyProfile).filter(FacultyProfile.email_public == current_user.email).first()
    if not f and current_user.full_name:
        f = db.query(FacultyProfile).filter(FacultyProfile.name.ilike(f"%{current_user.full_name}%")).first()
    
    if not f:
        raise HTTPException(status_code=404, detail="Faculty profile record not found.")

    if not f.user_id or f.user_id != current_user.id:
        f.user_id = current_user.id
        db.commit()
        db.refresh(f)

    return _serialize_faculty(f, current_user)


@router.put("/me")
def update_my_faculty_profile(
    payload: FacultyProfileUpdateRequest,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    f = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
    if not f:
        f = db.query(FacultyProfile).filter(FacultyProfile.email_public == current_user.email).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")

    if payload.bio is not None:
        f.bio = payload.bio
    if payload.officeLocation is not None:
        f.office_location = payload.officeLocation
    if payload.officeHours is not None:
        f.office_hours = payload.officeHours
    if payload.emailPublic is not None:
        f.email_public = payload.emailPublic
    if payload.phonePublic is not None:
        f.phone_public = payload.phonePublic
    if payload.areasOfExpertise is not None:
        f.areas_of_expertise = payload.areasOfExpertise
    if payload.externalLinks is not None:
        f.external_links_json = payload.externalLinks

    db.commit()

    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="FACULTY",
        action="UPDATE_FACULTY_PROFILE",
        target_entity="FacultyProfile",
        target_id=f.id,
        change_summary=f"Faculty member updated editable profile fields for {current_user.email}"
    )

    # Sync to Excel
    excel_service.sync_user_profile(db, current_user.id)

    # Broadcast real-time profile update
    realtime_manager.broadcast_event(
        event_type="faculty_profile_updated",
        data={
            "facultyId": f.id,
            "name": f.name,
            "department": f.department,
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
    )

    return {"message": "Faculty profile updated successfully."}


@router.get("/directory", response_model=List[FacultyProfileOut])
def get_faculty_directory(
    department: Optional[str] = Query(None),
    centre: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(FacultyProfile).filter(FacultyProfile.is_deleted == False)

    if department:
        dept_norm = department.strip().lower()
        if dept_norm in ["cai", "centre for artificial intelligence", "ai"]:
            query = query.filter(FacultyProfile.department.ilike("%Artificial Intelligence%"))
        elif dept_norm in ["cse", "computer science", "computer science & engineering"]:
            query = query.filter(FacultyProfile.department.ilike("%Computer Science%"))
        elif dept_norm in ["iot", "internet of things", "centre for internet of things"]:
            query = query.filter(
                (FacultyProfile.department.ilike("%Internet of Things%")) |
                (FacultyProfile.centre.ilike("%Internet of Things%"))
            )
        else:
            query = query.filter(FacultyProfile.department.ilike(f"%{department}%"))

    if centre:
        query = query.filter(FacultyProfile.centre.ilike(f"%{centre}%"))

    if search:
        search_norm = f"%{search.strip()}%"
        query = query.filter(
            (FacultyProfile.name.ilike(search_norm)) |
            (FacultyProfile.department.ilike(search_norm)) |
            (FacultyProfile.designation.ilike(search_norm)) |
            (FacultyProfile.qualification.ilike(search_norm))
        )

    faculty_rows = query.order_by(FacultyProfile.name.asc()).all()
    return [_serialize_faculty(f, current_user) for f in faculty_rows]


@router.get("/{faculty_id}", response_model=FacultyProfileOut)
def get_faculty_profile(
    faculty_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    f = db.query(FacultyProfile).filter(FacultyProfile.id == faculty_id).first()
    if not f:
        # Fallback query by user_id
        f = db.query(FacultyProfile).filter(FacultyProfile.user_id == faculty_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")

    return _serialize_faculty(f, current_user)
