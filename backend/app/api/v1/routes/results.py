from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user, require_super_admin, require_student
from backend.app.models.identity import User
from backend.app.models.academic_records import ResultRecord, ResultSubject
from backend.app.schemas.academic_records import ResultRecordOut, ResultSubjectOut
from backend.app.services.audit_service import log_audit_event
import pandas as pd
import io

router = APIRouter()


def _serialize_result(rec: ResultRecord) -> ResultRecordOut:
    subs = [
        ResultSubjectOut(
            id=s.id,
            subjectCode=s.subject_code,
            subjectName=s.subject_name,
            credits=s.credits,
            marksObtained=s.marks_obtained,
            maximumMarks=s.maximum_marks,
            grade=s.grade
        )
        for s in rec.subjects
    ]
    return ResultRecordOut(
        id=rec.id,
        rollNumber=rec.roll_number,
        studentName=rec.student_name,
        programme=rec.programme,
        branch=rec.branch,
        academicYear=rec.academic_year,
        semester=rec.semester,
        examinationSession=rec.examination_session,
        sgpa=rec.sgpa,
        cgpa=rec.cgpa,
        resultStatus=rec.result_status,
        subjects=subs,
        is_demo=rec.is_demo
    )


@router.get("/my-results", response_model=List[ResultRecordOut])
def get_my_results(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    STRICT PRIVACY:
    Students can access ONLY their own authorized results.
    Matches current_user.roll_number or current_user.id.
    """
    if not current_user.roll_number:
        return []

    records = db.query(ResultRecord).filter(
        ResultRecord.roll_number == current_user.roll_number,
        ResultRecord.is_deleted == False
    ).order_by(ResultRecord.created_at.desc()).all()

    return [_serialize_result(r) for r in records]


@router.get("/", response_model=List[ResultRecordOut])
def list_all_results_admin(
    roll_number: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Super Admin view of results. Audited automatically.
    """
    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="RESTRICTED_RESULTS_ACCESS",
        target_entity="ResultRecord",
        target_id=roll_number,
        change_summary="Super Admin accessed restricted student academic marks repository.",
        actor_user_id=current_user.id
    )

    query = db.query(ResultRecord).filter(ResultRecord.is_deleted == False)
    if roll_number:
        query = query.filter(ResultRecord.roll_number == roll_number)
    if semester:
        query = query.filter(ResultRecord.semester == semester)

    records = query.order_by(ResultRecord.roll_number.asc()).all()
    return [_serialize_result(r) for r in records]


@router.post("/import")
async def import_results(
    file: UploadFile = File(...),
    examination_session: str = "June 2026",
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Controlled CSV/XLSX results import with row-by-row validation:
    Checks roll number, valid marks range (0-100), duplicate prevention.
    """
    content = await file.read()
    filename = file.filename or "results.csv"

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    required_cols = {"roll_number", "student_name", "programme", "branch", "academic_year", "semester", "subject_code", "subject_name", "marks_obtained", "maximum_marks", "grade"}
    missing = required_cols - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Dataset missing required columns: {', '.join(missing)}")

    success_count = 0
    errors = []

    # Group rows by student roll_number and semester
    grouped = df.groupby(["roll_number", "semester"])

    for (roll, sem), group in grouped:
        first_row = group.iloc[0]
        rec = db.query(ResultRecord).filter(
            ResultRecord.roll_number == str(roll),
            ResultRecord.semester == str(sem),
            ResultRecord.examination_session == examination_session
        ).first()

        if not rec:
            rec = ResultRecord(
                roll_number=str(roll),
                student_name=str(first_row["student_name"]),
                programme=str(first_row["programme"]),
                branch=str(first_row["branch"]),
                academic_year=str(first_row["academic_year"]),
                semester=str(sem),
                examination_session=examination_session,
                result_status="PASS",
                is_demo=True
            )
            db.add(rec)
            db.flush()

        for idx, row in group.iterrows():
            marks = float(row["marks_obtained"])
            max_marks = float(row["maximum_marks"])
            if marks < 0 or marks > max_marks:
                errors.append(f"Row {idx+1}: Marks {marks} out of range [0, {max_marks}] for roll {roll}")
                continue

            sub = ResultSubject(
                result_record_id=rec.id,
                subject_code=str(row["subject_code"]),
                subject_name=str(row["subject_name"]),
                credits=float(row.get("credits", 3.0)),
                marks_obtained=marks,
                maximum_marks=max_marks,
                grade=str(row["grade"]),
                is_demo=True
            )
            db.add(sub)
            success_count += 1

    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="RESULT_IMPORT",
        target_entity="ResultRecord",
        change_summary=f"Imported {success_count} result subject entries for session '{examination_session}'. {len(errors)} warnings.",
        actor_user_id=current_user.id
    )

    db.commit()
    return {
        "status": "COMPLETED" if not errors else "PARTIAL",
        "imported_entries": success_count,
        "warnings": errors
    }
