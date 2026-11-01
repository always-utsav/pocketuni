from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class AudienceScopeInput(BaseModel):
    scopeType: str  # ENTIRE_INSTITUTION, CENTRE_FOR_AI, DEPARTMENT, PROGRAMME, BRANCH, ACADEMIC_YEAR, SEMESTER, BATCH, STUDENTS_ONLY, FACULTY_ONLY, SPECIFIC_ROLES, SPECIFIC_USERS
    scopeValue: Optional[str] = None


class ExtractedTableOut(BaseModel):
    id: str
    pageNumber: Optional[int] = None
    sheetName: Optional[str] = None
    tableIndex: int
    headers: List[str] = []
    rows: List[List[Any]] = []
    rowCount: int


class ExtractedContentOut(BaseModel):
    id: str
    pageNumber: Optional[int] = None
    heading: Optional[str] = None
    content: str
    contentType: str


class DocumentExtractionJobOut(BaseModel):
    id: str
    status: str
    extractorEngine: str
    pagesProcessed: int
    tablesFound: int
    warnings: List[str] = []
    errorMessage: Optional[str] = None
    executionTimeMs: int


class DocumentReviewOut(BaseModel):
    id: str
    title: str
    fileName: str
    filePath: str
    fileSizeBytes: int
    mimeType: str
    fileExtension: str
    contentHash: str
    category: str
    suggestedCategory: Optional[str] = None
    academicYear: Optional[str] = None
    semester: Optional[str] = None
    branch: Optional[str] = None
    programme: Optional[str] = None
    batch: Optional[str] = None
    issuingAuthority: Optional[str] = None
    status: str
    isCurrentPublished: bool
    currentVersionNo: int
    uploadedAt: str
    publishedAt: Optional[str] = None
    audiences: List[AudienceScopeInput] = []
    latestJob: Optional[DocumentExtractionJobOut] = None
    extractedContents: List[ExtractedContentOut] = []
    extractedTables: List[ExtractedTableOut] = []
    specializedData: Optional[Dict[str, Any]] = None
    warnings: List[str] = []
    is_demo: bool = False


class DocumentUpdateMetadata(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    academicYear: Optional[str] = None
    semester: Optional[str] = None
    branch: Optional[str] = None
    programme: Optional[str] = None
    batch: Optional[str] = None
    issuingAuthority: Optional[str] = None
    status: Optional[str] = None
    audiences: Optional[List[AudienceScopeInput]] = None


class DocumentPublishRequest(BaseModel):
    isAuthoritative: bool = True
    audiences: Optional[List[AudienceScopeInput]] = None
    changeSummary: Optional[str] = None


class DocumentListItemOut(BaseModel):
    id: str
    title: str
    fileName: str
    fileExtension: str
    fileSizeBytes: int
    category: str
    suggestedCategory: Optional[str] = None
    status: str
    academicYear: Optional[str] = None
    semester: Optional[str] = None
    branch: Optional[str] = None
    programme: Optional[str] = None
    batch: Optional[str] = None
    currentVersionNo: int
    isCurrentPublished: bool
    uploadedAt: str
    publishedAt: Optional[str] = None
    audiences: List[AudienceScopeInput] = []
    is_demo: bool = False


class MarksReconciliationRecord(BaseModel):
    enrollmentNumber: str
    studentName: str
    matchStatus: str  # MATCHED, UNMATCHED, DUPLICATE
    matchedUserId: Optional[str] = None
    matchedUserName: Optional[str] = None
    pageNumber: int
    columnsCount: int


class MarksReconciliationOut(BaseModel):
    documentId: str
    documentTitle: str
    totalRecords: int
    matchedCount: int
    unmatchedCount: int
    duplicateCount: int
    records: List[MarksReconciliationRecord] = []
    notice: str
