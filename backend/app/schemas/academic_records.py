from typing import List, Optional
from pydantic import BaseModel


class TimetableEntryOut(BaseModel):
    id: str
    day: str
    startTime: str
    endTime: str
    subject: str
    subjectCode: Optional[str] = None
    facultyName: Optional[str] = None
    room: Optional[str] = None
    programme: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[str] = None
    academicYear: Optional[str] = None
    is_demo: bool = True


class ExaminationEntryOut(BaseModel):
    id: str
    subject: str
    subjectCode: str
    date: str
    time: str
    examinationType: str
    semester: str
    programme: Optional[str] = None
    branch: Optional[str] = None
    academicYear: Optional[str] = None
    is_demo: bool = True


class AcademicCalendarEntryOut(BaseModel):
    id: str
    activity: str
    startDate: str
    endDate: Optional[str] = None
    applicableSemester: Optional[str] = None
    academicYear: str
    remarks: Optional[str] = None
    is_demo: bool = False


class ResultSubjectOut(BaseModel):
    id: str
    subjectCode: str
    subjectName: str
    credits: float
    marksObtained: float
    maximumMarks: float
    grade: str


class ResultRecordOut(BaseModel):
    id: str
    rollNumber: str
    studentName: str
    programme: str
    branch: str
    academicYear: str
    semester: str
    examinationSession: str
    sgpa: Optional[float] = None
    cgpa: Optional[float] = None
    resultStatus: str
    subjects: List[ResultSubjectOut] = []
    is_demo: bool = True
