from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class TimetableEntry(Base, CommonMixin):
    __tablename__ = "timetable_entries"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    day = Column(String(20), nullable=False)  # Monday, Tuesday, ...
    start_time = Column(String(20), nullable=False)  # '09:00 AM'
    end_time = Column(String(20), nullable=False)    # '10:00 AM'
    subject = Column(String(255), nullable=False)
    subject_code = Column(String(50), nullable=True)
    faculty_name = Column(String(255), nullable=True)
    room = Column(String(100), nullable=True)
    programme = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    semester = Column(String(20), nullable=True)
    academic_year = Column(String(50), nullable=True)
    effective_period = Column(String(100), nullable=True)


class ExaminationEntry(Base, CommonMixin):
    __tablename__ = "examination_entries"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    subject = Column(String(255), nullable=False)
    subject_code = Column(String(50), nullable=False)
    date = Column(String(50), nullable=False)
    time = Column(String(50), nullable=False)
    examination_type = Column(String(50), default="End-Semester", nullable=False)  # Mid-Term, End-Semester, Practical
    semester = Column(String(20), nullable=False)
    programme = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    academic_year = Column(String(50), nullable=True)


class AcademicCalendarEntry(Base, CommonMixin):
    __tablename__ = "academic_calendar_entries"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    activity = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=True)
    applicable_semester = Column(String(50), nullable=True)  # e.g., '2nd & 3rd Year' or 'Final Year'
    academic_year = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)


class ResultRecord(Base, CommonMixin):
    __tablename__ = "result_records"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    roll_number = Column(String(50), nullable=False, index=True)
    student_name = Column(String(255), nullable=False)
    programme = Column(String(100), nullable=False)
    branch = Column(String(100), nullable=False)
    academic_year = Column(String(50), nullable=False)
    semester = Column(String(20), nullable=False)
    examination_session = Column(String(100), nullable=False)  # 'June 2026', 'Dec 2026'
    sgpa = Column(Float, nullable=True)
    cgpa = Column(Float, nullable=True)
    result_status = Column(String(50), default="PASS", nullable=False)  # PASS, FAIL, ATKT, WITHHELD

    subjects = relationship("ResultSubject", back_populates="result_record", cascade="all, delete-orphan")


class ResultSubject(Base, CommonMixin):
    __tablename__ = "result_subjects"

    result_record_id = Column(String(36), ForeignKey("result_records.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_code = Column(String(50), nullable=False)
    subject_name = Column(String(255), nullable=False)
    credits = Column(Float, default=3.0, nullable=False)
    marks_obtained = Column(Float, nullable=False)
    maximum_marks = Column(Float, default=100.0, nullable=False)
    grade = Column(String(10), nullable=False)  # O, A+, A, B+, B, C, P, F

    result_record = relationship("ResultRecord", back_populates="subjects")
