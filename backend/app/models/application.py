from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class Application(Base, CommonMixin):
    __tablename__ = "applications"

    student_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    faculty_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    chat_id = Column(String(36), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # leave, bonafide, permission, noc, fee, general
    status = Column(String(50), default="draft", nullable=False, index=True)  # draft, sent, approved, rejected
    current_version_no = Column(Integer, default=1, nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    decision_note = Column(Text, nullable=True)

    # Relationships
    student = relationship("User", back_populates="applications", foreign_keys=[student_id])
    faculty = relationship("User", back_populates="assigned_applications", foreign_keys=[faculty_id])
    versions = relationship("ApplicationVersionModel", back_populates="application", cascade="all, delete-orphan")
    status_history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")
    shares = relationship("ApplicationShare", back_populates="application", cascade="all, delete-orphan")
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")


class ApplicationVersionModel(Base, CommonMixin):
    __tablename__ = "application_versions"

    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    version_no = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_by_role = Column(String(50), default="student", nullable=False)  # 'student' | 'ai'

    application = relationship("Application", back_populates="versions")


class ApplicationStatusHistory(Base, CommonMixin):
    __tablename__ = "application_status_history"

    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(50), nullable=False)
    to_status = Column(String(50), nullable=False)
    actor_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_name = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)

    application = relationship("Application", back_populates="status_history")


class ApplicationShare(Base, CommonMixin):
    __tablename__ = "application_shares"

    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    shared_with_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    shared_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_level = Column(String(50), default="review", nullable=False)  # 'view', 'review', 'decide'

    application = relationship("Application", back_populates="shares")


class ApplicationDocument(Base, CommonMixin):
    __tablename__ = "application_documents"

    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)

    application = relationship("Application", back_populates="documents")


class ApplicationOutbox(Base, CommonMixin):
    __tablename__ = "application_outbox"

    data_source = Column(String(50), default="official", nullable=False)
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(50), default="QUEUED", nullable=False, index=True)  # QUEUED, SENT_TO_PROVIDER, DELIVERED, FAILED
    provider_response = Column(Text, nullable=True)
    attempt_count = Column(Integer, default=0, nullable=False)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)

