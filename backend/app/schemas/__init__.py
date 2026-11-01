from backend.app.schemas.auth import (
    Token,
    TokenPayload,
    LocalDevLoginRequest,
    CurrentUserResponse,
)
from backend.app.schemas.student import (
    SkillSchema,
    ProjectSchema,
    StudentProfileUpdate,
    StudentMatchCardSchema,
)
from backend.app.schemas.faculty import (
    FacultyPublicationSchema,
    FacultyProfileOut,
)
from backend.app.schemas.application import (
    ApplicationStatusHistoryOut,
    ApplicationVersionOut,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationDecisionRequest,
    ApplicationShareRequest,
    ApplicationOut,
)
from backend.app.schemas.document import (
    AudienceScopeInput,
    ExtractedTableOut,
    ExtractedContentOut,
    DocumentExtractionJobOut,
    DocumentReviewOut,
    DocumentUpdateMetadata,
    DocumentPublishRequest,
    DocumentListItemOut,
)
from backend.app.schemas.academic_records import (
    TimetableEntryOut,
    ExaminationEntryOut,
    AcademicCalendarEntryOut,
    ResultSubjectOut,
    ResultRecordOut,
)
from backend.app.schemas.admin import (
    AuditLogOut,
    AdminStatsOut,
    SystemHealthOut,
    ImportJobOut,
)
from backend.app.schemas.communication import (
    MessageSourceOut,
    MessageOut,
    ChatOut,
    MessageCreate,
    FeedbackCreate,
    NotificationOut,
)
