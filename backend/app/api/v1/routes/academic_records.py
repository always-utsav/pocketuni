from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user
from backend.app.models.identity import User
from backend.app.models.academic_records import (
    TimetableEntry,
    ExaminationEntry,
    AcademicCalendarEntry,
)
from backend.app.schemas.academic_records import (
    TimetableEntryOut,
    ExaminationEntryOut,
    AcademicCalendarEntryOut,
)

router = APIRouter()


@router.get("/timetables", response_model=List[TimetableEntryOut])
def get_timetables(
    day: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TimetableEntry).filter(TimetableEntry.is_deleted == False)

    # If student, default filter to student's branch/semester if available
    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    if "STUDENT" in user_roles and not branch and current_user.branch:
        query = query.filter(TimetableEntry.branch.ilike(f"%{current_user.branch}%"))
    elif branch:
        query = query.filter(TimetableEntry.branch.ilike(f"%{branch}%"))

    if day:
        query = query.filter(TimetableEntry.day.ilike(f"%{day}%"))
    if semester:
        query = query.filter(TimetableEntry.semester == semester)

    rows = query.order_by(TimetableEntry.day.asc(), TimetableEntry.start_time.asc()).all()
    return [
        TimetableEntryOut(
            id=r.id,
            day=r.day,
            startTime=r.start_time,
            endTime=r.end_time,
            subject=r.subject,
            subjectCode=r.subject_code,
            facultyName=r.faculty_name,
            room=r.room,
            programme=r.programme,
            branch=r.branch,
            semester=r.semester,
            academicYear=r.academic_year,
            is_demo=r.is_demo
        )
        for r in rows
    ]


@router.get("/datesheets", response_model=List[ExaminationEntryOut])
def get_examination_datesheets(
    semester: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ExaminationEntry).filter(ExaminationEntry.is_deleted == False)
    if semester:
        query = query.filter(ExaminationEntry.semester == semester)
    if branch:
        query = query.filter(ExaminationEntry.branch.ilike(f"%{branch}%"))

    rows = query.order_by(ExaminationEntry.date.asc(), ExaminationEntry.time.asc()).all()
    return [
        ExaminationEntryOut(
            id=r.id,
            subject=r.subject,
            subjectCode=r.subject_code,
            date=r.date,
            time=r.time,
            examinationType=r.examination_type,
            semester=r.semester,
            programme=r.programme,
            branch=r.branch,
            academicYear=r.academic_year,
            is_demo=r.is_demo
        )
        for r in rows
    ]


@router.get("/calendars", response_model=List[AcademicCalendarEntryOut])
def get_academic_calendars(
    year_group: Optional[str] = Query(None, description="'2nd & 3rd Year' or 'Final Year'"),
    academic_year: Optional[str] = Query("2026-2027"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns official MITS Academic Calendar entries for 2026-2027.
    Distinguishes second/third-year and final-year schedules per Section 9.
    """
    query = db.query(AcademicCalendarEntry).filter(
        AcademicCalendarEntry.is_deleted == False,
        AcademicCalendarEntry.academic_year == academic_year
    )
    if year_group:
        query = query.filter(AcademicCalendarEntry.applicable_semester.ilike(f"%{year_group}%"))

    rows = query.order_by(AcademicCalendarEntry.start_date.asc()).all()
    return [
        AcademicCalendarEntryOut(
            id=r.id,
            activity=r.activity,
            startDate=r.start_date,
            endDate=r.end_date,
            applicableSemester=r.applicable_semester,
            academicYear=r.academic_year,
            remarks=r.remarks,
            is_demo=r.is_demo
        )
        for r in rows
    ]
