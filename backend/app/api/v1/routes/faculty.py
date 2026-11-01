from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user, require_faculty
from backend.app.models.identity import User
from backend.app.models.faculty import FacultyProfile, FacultyPublication, FacultyResearchInterest
from backend.app.schemas.faculty import FacultyProfileOut, FacultyPublicationSchema
from backend.app.services.audit_service import log_audit_event
from backend.app.services.excel_service import excel_service

router = APIRouter()


class FacultyProfileUpdate(BaseModel):
    bio: Optional[str] = None
    officeLocation: Optional[str] = None
    officeHours: Optional[str] = None
    emailPublic: Optional[str] = None
    phonePublic: Optional[str] = None
    photoUrl: Optional[str] = None
    researchAreas: Optional[List[str]] = None
    areasOfExpertise: Optional[List[str]] = None


@router.get("/me")
def get_my_faculty_profile(
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    f = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
    if not f:
        # Fallback by email
        f = db.query(FacultyProfile).filter(FacultyProfile.email_public == current_user.email).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty profile record not found.")

    pubs = [
        FacultyPublicationSchema(
            title=p.title,
            journal=p.journal,
            year=p.year,
            doi=p.doi
        )
        for p in f.publications
    ]
    areas = [r.area for r in f.research_interests]

    return {
        "facultyId": f.id,
        "facultyIdentifier": f.faculty_identifier or "",
        "name": f.name,
        "designation": f.designation,
        "department": f.department,
        "centre": f.centre or f.department,
        "qualification": f.qualification or "",
        "officialProfileUrl": f.official_profile_url or "",
        "researchAreas": areas,
        "areasOfExpertise": f.areas_of_expertise or [],
        "publications": pubs,
        "courses": f.courses or [],
        "emailPublic": f.email_public or current_user.email,
        "phonePublic": f.phone_public or "",
        "officeLocation": f.office_location or "",
        "officeHours": f.office_hours or "",
        "photoUrl": f.photo_url or current_user.picture_url,
        "bio": f.bio or "",
        "sourceUrl": f.source_url or "",
        "verificationStatus": f.verification_status,
        "isMentor": f.is_mentor,
        "dataSource": f.data_source,
        "is_demo": f.is_demo
    }


@router.put("/me")
def update_my_faculty_profile(
    payload: FacultyProfileUpdate,
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
    if payload.photoUrl is not None:
        f.photo_url = payload.photoUrl
    if payload.areasOfExpertise is not None:
        f.areas_of_expertise = payload.areasOfExpertise

    if payload.researchAreas is not None:
        db.query(FacultyResearchInterest).filter(FacultyResearchInterest.faculty_profile_id == f.id).delete()
        for area in payload.researchAreas:
            if area.strip():
                db.add(FacultyResearchInterest(faculty_profile_id=f.id, area=area.strip(), is_demo=f.is_demo))

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

    return {"message": "Faculty profile updated successfully."}


@router.get("/directory", response_model=List[FacultyProfileOut])
def get_faculty_directory(
    department: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(FacultyProfile).filter(FacultyProfile.is_deleted == False)

    if department:
        query = query.filter(FacultyProfile.department.ilike(f"%{department}%"))

    if search:
        search_norm = f"%{search}%"
        query = query.filter(
            (FacultyProfile.name.ilike(search_norm)) |
            (FacultyProfile.department.ilike(search_norm)) |
            (FacultyProfile.designation.ilike(search_norm))
        )

    faculty_rows = query.order_by(FacultyProfile.name.asc()).all()
    results = []

    for f in faculty_rows:
        pubs = [
            FacultyPublicationSchema(
                title=p.title,
                journal=p.journal,
                year=p.year,
                doi=p.doi
            )
            for p in f.publications
        ]
        areas = [r.area for r in f.research_interests]

        results.append(
            FacultyProfileOut(
                facultyId=f.id,
                name=f.name,
                designation=f.designation,
                department=f.department,
                qualification=f.qualification,
                researchAreas=areas,
                publications=pubs,
                emailPublic=f.email_public,
                phonePublic=f.phone_public,
                officeLocation=f.office_location,
                officeHours=f.office_hours,
                photoUrl=f.photo_url,
                bio=f.bio,
                sourceUrl=f.source_url,
                verificationStatus=f.verification_status,
                isMentor=f.is_mentor,
                is_demo=f.is_demo
            )
        )

    return results


@router.get("/{faculty_id}", response_model=FacultyProfileOut)
def get_faculty_profile(
    faculty_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    f = db.query(FacultyProfile).filter(FacultyProfile.id == faculty_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")

    pubs = [
        FacultyPublicationSchema(
            title=p.title,
            journal=p.journal,
            year=p.year,
            doi=p.doi
        )
        for p in f.publications
    ]
    areas = [r.area for r in f.research_interests]

    return FacultyProfileOut(
        facultyId=f.id,
        name=f.name,
        designation=f.designation,
        department=f.department,
        qualification=f.qualification,
        researchAreas=areas,
        publications=pubs,
        emailPublic=f.email_public,
        phonePublic=f.phone_public,
        officeLocation=f.office_location,
        officeHours=f.office_hours,
        photoUrl=f.photo_url,
        bio=f.bio,
        sourceUrl=f.source_url,
        verificationStatus=f.verification_status,
        isMentor=f.is_mentor,
        is_demo=f.is_demo
    )
