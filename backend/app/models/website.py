from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class InstitutionalSource(Base, CommonMixin):
    __tablename__ = "institutional_sources"

    domain = Column(String(255), nullable=False, index=True)
    base_url = Column(String(500), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), default="MITS_MAIN", nullable=False, index=True)  # MITS_MAIN, AMS, E_GOVERNANCE, DEPARTMENT, PORTAL
    crawl_status = Column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, PAUSED, RESTRICTED, FAILED
    crawl_depth = Column(Integer, default=2, nullable=False)
    crawl_frequency_hours = Column(Integer, default=24, nullable=False)
    last_crawled_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    auth_required = Column(Boolean, default=False, nullable=False)
    allowed_patterns = Column(JSON, default=list, nullable=False)
    excluded_patterns = Column(JSON, default=list, nullable=False)
    description = Column(Text, nullable=True)

    pages = relationship("SourcePage", back_populates="source", cascade="all, delete-orphan")
    crawl_runs = relationship("CrawlRun", back_populates="source", cascade="all, delete-orphan")


class SourcePage(Base, CommonMixin):
    __tablename__ = "source_pages"

    source_id = Column(String(36), ForeignKey("institutional_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(1000), nullable=False, unique=True, index=True)
    canonical_url = Column(String(1000), nullable=True)
    title = Column(String(500), nullable=True)
    page_type = Column(String(50), default="GENERAL", nullable=False, index=True)  # ACADEMIC, FACULTY, NOTICE, TIMETABLE, PORTAL_INFO, RESEARCH, ADMISSIONS, PLACEMENTS, GENERAL
    department_name = Column(String(150), nullable=True, index=True)
    content_hash = Column(String(64), nullable=False, index=True)
    http_status = Column(Integer, default=200, nullable=False)
    raw_html = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
    version_no = Column(Integer, default=1, nullable=False)
    is_superseded = Column(Boolean, default=False, nullable=False, index=True)
    superseded_by_id = Column(String(36), nullable=True)
    verification_status = Column(String(50), default="VERIFIED_OFFICIAL_SOURCE", nullable=False)
    retrieved_at = Column(DateTime(timezone=True), nullable=False)
    last_crawled_at = Column(DateTime(timezone=True), nullable=False)

    source = relationship("InstitutionalSource", back_populates="pages")
    documents = relationship("ExtractedWebDocument", back_populates="source_page", cascade="all, delete-orphan")


class CrawlRun(Base, CommonMixin):
    __tablename__ = "crawl_runs"

    source_id = Column(String(36), ForeignKey("institutional_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="RUNNING", nullable=False)  # RUNNING, COMPLETED, PARTIAL, FAILED, STOPPED
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    pages_discovered = Column(Integer, default=0, nullable=False)
    pages_crawled = Column(Integer, default=0, nullable=False)
    pdfs_found = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    summary_json = Column(JSON, default=dict, nullable=False)

    source = relationship("InstitutionalSource", back_populates="crawl_runs")


class ExtractedWebDocument(Base, CommonMixin):
    __tablename__ = "extracted_web_documents"

    source_page_id = Column(String(36), ForeignKey("source_pages.id", ondelete="CASCADE"), nullable=False, index=True)
    file_url = Column(String(1000), nullable=False)
    title = Column(String(500), nullable=False)
    doc_type = Column(String(50), default="PDF", nullable=False)
    file_path = Column(String(500), nullable=True)
    content_hash = Column(String(64), nullable=True)
    extracted_text = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    is_indexed = Column(Boolean, default=False, nullable=False)

    source_page = relationship("SourcePage", back_populates="documents")


class InstitutionalPortal(Base, CommonMixin):
    __tablename__ = "institutional_portals"

    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)  # ACADEMIC, EXAMINATION, LEARNING, FACULTY_STAFF, STUDENT_SERVICES, RESEARCH, ADMISSIONS, PLACEMENTS, ALUMNI
    official_url = Column(String(500), nullable=False, unique=True)
    domain = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    services_description = Column(Text, nullable=True)
    auth_required = Column(Boolean, default=True, nullable=False)
    contains_confidential_records = Column(Boolean, default=True, nullable=False)
    integration_status = Column(String(50), default="LINK_ONLY", nullable=False)  # LINK_ONLY, APPROVED_IMPORT_ONLY, API_PLANNED, ACTIVE_ADAPTER
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
