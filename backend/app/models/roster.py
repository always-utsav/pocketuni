from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON, DateTime
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class RosterImportBatch(Base, CommonMixin):
    __tablename__ = "roster_import_batches"

    entity_type = Column(String(50), nullable=False, index=True)  # STUDENT, FACULTY
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(String(50), default="COMPLETED", nullable=False)  # PENDING, VALIDATED, COMPLETED, FAILED
    total_records = Column(Integer, default=0, nullable=False)
    successful_records = Column(Integer, default=0, nullable=False)
    failed_records = Column(Integer, default=0, nullable=False)
    errors_summary = Column(JSON, default=list, nullable=False)
    imported_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class ExcelSyncJob(Base, CommonMixin):
    __tablename__ = "excel_sync_jobs"

    entity_type = Column(String(50), nullable=False, index=True)  # STUDENT, FACULTY
    entity_id = Column(String(36), nullable=False, index=True)
    user_email = Column(String(255), nullable=False, index=True)
    target_file = Column(String(255), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, PROCESSING, COMPLETED, FAILED
    retry_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
