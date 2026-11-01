from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: str
    actorEmail: str
    actorRole: str
    action: str
    targetEntity: str
    targetId: Optional[str] = None
    changeSummary: str
    ipAddress: Optional[str] = None
    createdAt: str


class AdminStatsOut(BaseModel):
    totalStudents: int
    totalFaculty: int
    totalDocuments: int
    publishedDocuments: int
    pendingReviewDocuments: int
    totalApplications: int
    pendingApplications: int
    totalAudits: int


class SystemHealthOut(BaseModel):
    status: str
    database: str
    storageAccessible: bool
    ocrAvailable: bool
    environment: str
    version: str


class ImportJobOut(BaseModel):
    id: str
    entityType: str
    fileName: str
    status: str
    totalRows: int
    successfulRows: int
    failedRows: int
    createdAt: str
