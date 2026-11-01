from typing import List, Optional
from pydantic import BaseModel


class ApplicationStatusHistoryOut(BaseModel):
    id: str
    fromStatus: str
    toStatus: str
    actorUserId: Optional[str] = None
    actorName: str
    note: Optional[str] = None
    createdAt: str


class ApplicationVersionOut(BaseModel):
    id: str
    versionNo: int
    content: str
    createdBy: str
    createdAt: str


class ApplicationCreate(BaseModel):
    title: str
    type: str  # leave, bonafide, permission, noc, fee, general
    content: str
    facultyId: Optional[str] = None
    chatId: Optional[str] = None


class ApplicationUpdate(BaseModel):
    content: Optional[str] = None
    title: Optional[str] = None


class ApplicationDecisionRequest(BaseModel):
    decision: str  # 'approved' or 'rejected'
    note: Optional[str] = None


class ApplicationShareRequest(BaseModel):
    facultyId: str
    note: Optional[str] = None


class ApplicationOut(BaseModel):
    id: str
    studentId: str
    studentName: str
    studentEmail: str
    studentRollNumber: Optional[str] = None
    studentBranch: Optional[str] = None
    studentYear: int
    facultyId: Optional[str] = None
    facultyName: Optional[str] = None
    facultyDepartment: Optional[str] = None
    chatId: Optional[str] = None
    title: str
    type: str
    status: str
    currentVersionId: str
    content: str
    versions: List[ApplicationVersionOut] = []
    statusHistory: List[ApplicationStatusHistoryOut] = []
    createdAt: str
    sentAt: Optional[str] = None
    decidedAt: Optional[str] = None
    decisionNote: Optional[str] = None
    is_demo: bool = True
