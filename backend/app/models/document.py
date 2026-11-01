from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class InstitutionalDocument(Base, CommonMixin):
    __tablename__ = "institutional_documents"

    title = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(20), nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    
    # Classification & Academic scope
    category = Column(String(50), default="OTHER", nullable=False, index=True)
    suggested_category = Column(String(50), nullable=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year = Column(String(50), nullable=True)
    semester = Column(String(20), nullable=True)
    branch = Column(String(100), nullable=True)
    programme = Column(String(100), nullable=True)
    batch = Column(String(50), nullable=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    issuing_authority = Column(String(255), nullable=True)

    # Status workflow
    # DRAFT, UPLOADED, PROCESSING, EXTRACTION_FAILED, NEEDS_REVIEW, READY_TO_PUBLISH, PUBLISHED, SUPERSEDED, ARCHIVED
    status = Column(String(50), default="UPLOADED", nullable=False, index=True)
    is_current_published = Column(Boolean, default=False, nullable=False, index=True)
    current_version_no = Column(Integer, default=1, nullable=False)
    
    # Knowledge Indexing & Embedding status
    # NOT_INDEXED, PENDING, PROCESSING, INDEXED, PARTIAL, FAILED, NEEDS_REINDEX
    indexing_status = Column(String(50), default="NOT_INDEXED", nullable=False, index=True)
    indexed_chunks_count = Column(Integer, default=0, nullable=False)
    embedding_model = Column(String(100), nullable=True)
    indexed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Uploaded by
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    published_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    audiences = relationship("DocumentAudience", back_populates="document", cascade="all, delete-orphan")
    extraction_jobs = relationship("DocumentExtractionJob", back_populates="document", cascade="all, delete-orphan")
    extracted_contents = relationship("ExtractedDocumentContent", back_populates="document", cascade="all, delete-orphan")
    extracted_tables = relationship("ExtractedTable", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    publication_histories = relationship("DocumentPublicationHistory", back_populates="document", cascade="all, delete-orphan")
    source = relationship("DocumentSource", back_populates="document", uselist=False, cascade="all, delete-orphan")


class DocumentVersion(Base, CommonMixin):
    __tablename__ = "document_versions"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_no = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    content_hash = Column(String(64), nullable=False)
    change_summary = Column(Text, nullable=True)
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    superseded_version_id = Column(String(36), nullable=True)

    document = relationship("InstitutionalDocument", back_populates="versions")


class DocumentAudience(Base, CommonMixin):
    __tablename__ = "document_audiences"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    # Scope types: 'ENTIRE_INSTITUTION', 'CENTRE_FOR_AI', 'DEPARTMENT', 'PROGRAMME', 'BRANCH', 'ACADEMIC_YEAR', 'SEMESTER', 'BATCH', 'STUDENTS_ONLY', 'FACULTY_ONLY', 'SPECIFIC_USERS'
    scope_type = Column(String(50), nullable=False, index=True)
    scope_value = Column(String(255), nullable=True)  # e.g., 'Centre for AI', '3rd Year', '5th Semester'

    document = relationship("InstitutionalDocument", back_populates="audiences")


class DocumentExtractionJob(Base, CommonMixin):
    __tablename__ = "document_extraction_jobs"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    # State: PENDING, PROCESSING, COMPLETED, PARTIAL, FAILED
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    extractor_engine = Column(String(50), nullable=False)  # pdfplumber, python-docx, openpyxl, pandas, txt, ocr_tesseract
    pages_processed = Column(Integer, default=0, nullable=False)
    tables_found = Column(Integer, default=0, nullable=False)
    warnings = Column(JSON, default=list, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, default=0, nullable=False)

    document = relationship("InstitutionalDocument", back_populates="extraction_jobs")


class ExtractedDocumentContent(Base, CommonMixin):
    __tablename__ = "extracted_document_contents"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    heading = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="paragraph", nullable=False)  # paragraph, heading, list, table_summary

    document = relationship("InstitutionalDocument", back_populates="extracted_contents")


class ExtractedTable(Base, CommonMixin):
    __tablename__ = "extracted_tables"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    sheet_name = Column(String(100), nullable=True)
    table_index = Column(Integer, default=0, nullable=False)
    headers = Column(JSON, default=list, nullable=False)
    rows = Column(JSON, default=list, nullable=False)
    row_count = Column(Integer, default=0, nullable=False)

    document = relationship("InstitutionalDocument", back_populates="extracted_tables")


class DocumentPublicationHistory(Base, CommonMixin):
    __tablename__ = "document_publication_histories"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'PUBLISHED', 'UNPUBLISHED', 'SUPERSEDED', 'ARCHIVED'
    actor_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note = Column(Text, nullable=True)

    document = relationship("InstitutionalDocument", back_populates="publication_histories")


class DocumentSource(Base, CommonMixin):
    __tablename__ = "document_sources"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    source_url = Column(String(500), nullable=True)
    source_category = Column(String(100), nullable=True)
    retrieval_date = Column(DateTime(timezone=True), nullable=True)
    verification_status = Column(String(50), default="VERIFIED_OFFICIAL_SOURCE", nullable=False)

    document = relationship("InstitutionalDocument", back_populates="source")


class DocumentChunk(Base, CommonMixin):
    __tablename__ = "document_chunks"

    document_id = Column(String(36), ForeignKey("institutional_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(String(36), nullable=True, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, default=0, nullable=False)
    source_page_number = Column(Integer, nullable=True)
    source_section = Column(String(255), nullable=True)
    
    # Academic & Scope metadata for pre-retrieval filtering
    category = Column(String(50), nullable=False, index=True)
    academic_year = Column(String(50), nullable=True)
    department_id = Column(String(36), nullable=True, index=True)
    programme = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    semester = Column(String(20), nullable=True, index=True)
    batch = Column(String(50), nullable=True)
    publication_status = Column(String(50), default="PUBLISHED", nullable=False, index=True)
    is_current = Column(Boolean, default=True, nullable=False, index=True)
    audience_metadata = Column(JSON, default=list, nullable=False)
    
    # Vector embedding information
    embedding_model = Column(String(100), nullable=False)
    embedding_dimension = Column(Integer, nullable=False)
    embedding_json = Column(JSON, nullable=False)  # stored as list of float numbers

    document = relationship("InstitutionalDocument", back_populates="chunks")
