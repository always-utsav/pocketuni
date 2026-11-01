from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, DateTime
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class AuditLog(Base, CommonMixin):
    __tablename__ = "audit_logs"

    actor_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_email = Column(String(255), nullable=False, index=True)
    actor_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    target_entity = Column(String(100), nullable=False, index=True)
    target_id = Column(String(100), nullable=True)
    change_summary = Column(Text, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    extra_context = Column(JSON, default=dict, nullable=False)


class AdminConfiguration(Base, CommonMixin):
    __tablename__ = "admin_configurations"

    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    is_sensitive = Column(Integer, default=0, nullable=False)


class ImportJob(Base, CommonMixin):
    __tablename__ = "import_jobs"

    entity_type = Column(String(50), nullable=False, index=True)  # students, faculty, departments, programmes, results
    file_name = Column(String(255), nullable=False)
    status = Column(String(50), default="PROCESSING", nullable=False)  # PENDING, PROCESSING, COMPLETED, PARTIAL, FAILED
    total_rows = Column(Integer, default=0, nullable=False)
    successful_rows = Column(Integer, default=0, nullable=False)
    failed_rows = Column(Integer, default=0, nullable=False)
    performed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class ImportErrorRecord(Base, CommonMixin):
    __tablename__ = "import_errors"

    import_job_id = Column(String(36), ForeignKey("import_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    raw_data = Column(JSON, default=dict, nullable=False)
    error_message = Column(Text, nullable=False)
