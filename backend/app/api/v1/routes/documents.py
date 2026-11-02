import os
import re
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user, require_super_admin
from backend.app.models.identity import User
from backend.app.models.document import (
    InstitutionalDocument,
    DocumentVersion,
    DocumentAudience,
    DocumentExtractionJob,
    ExtractedDocumentContent,
    ExtractedTable,
    DocumentPublicationHistory,
)
from backend.app.schemas.document import (
    DocumentReviewOut,
    DocumentListItemOut,
    DocumentUpdateMetadata,
    DocumentPublishRequest,
    AudienceScopeInput,
    ExtractedContentOut,
    ExtractedTableOut,
    DocumentExtractionJobOut,
    MarksReconciliationOut,
    MarksReconciliationRecord,
)
from backend.app.services.storage_service import storage_service
from backend.app.services.extraction_service import extraction_engine
from backend.app.services.classification_service import classification_service
from backend.app.services.audience_service import audience_service
from backend.app.services.audit_service import log_audit_event

router = APIRouter()


def _serialize_doc_review(doc: InstitutionalDocument) -> DocumentReviewOut:
    audiences = [
        AudienceScopeInput(scopeType=a.scope_type, scopeValue=a.scope_value)
        for a in doc.audiences
    ]
    latest_job = doc.extraction_jobs[-1] if doc.extraction_jobs else None
    job_out = None
    if latest_job:
        job_out = DocumentExtractionJobOut(
            id=latest_job.id,
            status=latest_job.status,
            extractorEngine=latest_job.extractor_engine,
            pagesProcessed=latest_job.pages_processed,
            tablesFound=latest_job.tables_found,
            warnings=latest_job.warnings or [],
            errorMessage=latest_job.error_message,
            executionTimeMs=latest_job.execution_time_ms
        )

    contents = [
        ExtractedContentOut(
            id=c.id,
            pageNumber=c.page_number,
            heading=c.heading,
            content=c.content,
            contentType=c.content_type
        )
        for c in doc.extracted_contents
    ]

    tables = [
        ExtractedTableOut(
            id=t.id,
            pageNumber=t.page_number,
            sheetName=t.sheet_name,
            tableIndex=t.table_index,
            headers=t.headers or [],
            rows=t.rows or [],
            rowCount=t.row_count
        )
        for t in doc.extracted_tables
    ]

    return DocumentReviewOut(
        id=doc.id,
        title=doc.title,
        fileName=doc.file_name,
        filePath=doc.file_path,
        fileSizeBytes=doc.file_size_bytes,
        mimeType=doc.mime_type,
        fileExtension=doc.file_extension,
        contentHash=doc.content_hash,
        category=doc.category,
        suggestedCategory=doc.suggested_category,
        academicYear=doc.academic_year,
        semester=doc.semester,
        branch=doc.branch,
        programme=doc.programme,
        batch=doc.batch,
        issuingAuthority=doc.issuing_authority,
        status=doc.status,
        isCurrentPublished=doc.is_current_published,
        currentVersionNo=doc.current_version_no,
        uploadedAt=doc.created_at.isoformat(),
        publishedAt=doc.published_at.isoformat() if doc.published_at else None,
        audiences=audiences,
        latestJob=job_out,
        extractedContents=contents,
        extractedTables=tables,
        warnings=latest_job.warnings if latest_job else [],
        is_demo=doc.is_demo
    )


@router.post("/upload", response_model=DocumentReviewOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    academic_year: Optional[str] = Form(None),
    semester: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    programme: Optional[str] = Form(None),
    batch: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Ingest, store, extract, and classify an official institutional document.
    Never automatically publishes the document.
    Defaults to NEEDS_REVIEW status.
    """
    saved_metadata = await storage_service.save_file(
        upload_file=file,
        subfolder="institutional_documents"
    )

    doc_title = title or file.filename or "Untitled Document"
    file_size = saved_metadata["file_size_bytes"]

    # Check for duplicate document content hash
    existing_doc = db.query(InstitutionalDocument).filter(
        InstitutionalDocument.content_hash == saved_metadata["content_hash"],
        InstitutionalDocument.is_deleted == False
    ).first()

    version_no = 1
    if existing_doc:
        version_no = existing_doc.current_version_no + 1

    doc = InstitutionalDocument(
        title=doc_title,
        file_name=saved_metadata["file_name"],
        file_path=saved_metadata["storage_rel_path"],
        file_size_bytes=file_size,
        mime_type=saved_metadata["mime_type"],
        file_extension=saved_metadata["file_extension"],
        content_hash=saved_metadata["content_hash"],
        status="PROCESSING",
        current_version_no=version_no,
        uploaded_by_user_id=current_user.id,
        is_demo=False
    )
    db.add(doc)
    db.flush()

    # Track version in document_versions table
    db.add(DocumentVersion(
        document_id=doc.id,
        version_no=version_no,
        file_name=saved_metadata["file_name"],
        file_path=saved_metadata["storage_rel_path"],
        content_hash=saved_metadata["content_hash"],
        change_summary="Initial upload" if version_no == 1 else f"Revision version {version_no}"
    ))

    # Trigger extraction engine
    full_local_path = saved_metadata["absolute_path"]
    extraction_res = extraction_engine.extract(full_local_path, saved_metadata["mime_type"])

    # Persist extraction job telemetry
    job = DocumentExtractionJob(
        document_id=doc.id,
        extractor_engine=extraction_res.extractor_engine,
        status=extraction_res.status,
        pages_processed=extraction_res.pages_processed,
        tables_found=extraction_res.tables_found,
        execution_time_ms=extraction_res.execution_time_ms,
        warnings=extraction_res.warnings,
        error_message=extraction_res.error_message
    )
    db.add(job)
    db.flush()

    # Persist extracted content blocks
    for item in extraction_res.contents:
        db.add(ExtractedDocumentContent(
            document_id=doc.id,
            page_number=item.get("page_number"),
            heading=item.get("heading"),
            content=item.get("content", ""),
            content_type=item.get("content_type", "paragraph")
        ))

    # Persist extracted tables
    for tbl in extraction_res.tables:
        db.add(ExtractedTable(
            document_id=doc.id,
            page_number=tbl.get("page_number"),
            sheet_name=tbl.get("sheet_name"),
            table_index=tbl.get("table_index", 1),
            headers=tbl.get("headers", []),
            rows=tbl.get("rows", []),
            row_count=tbl.get("row_count", 0)
        ))

    # Automated heuristic classification & metadata inference
    classification = classification_service.classify_and_extract_metadata(
        title=doc_title,
        contents=extraction_res.contents,
        tables=extraction_res.tables,
        source_filename=file.filename or ""
    )

    doc.suggested_category = classification["category"]
    doc.category = category or classification["category"]
    doc.academic_year = academic_year or classification["academic_year"]
    doc.semester = semester or classification["semester"]
    doc.programme = (programme or classification.get("programme") or "")[:100] or None
    doc.branch = (branch or classification.get("branch") or "")[:100] or None
    doc.batch = (batch or classification.get("batch") or "")[:50] or None
    doc.issuing_authority = (issuing_authority or classification.get("issuing_institution") or "")[:255] or None
    doc.status = "NEEDS_REVIEW" if extraction_res.status != "FAILED" else "EXTRACTION_FAILED"

    # Audience assignment: INTERNAL_MARKS defaults to Super Admin ONLY
    if doc.category == "INTERNAL_MARKS":
        db.add(DocumentAudience(
            document_id=doc.id,
            scope_type="SPECIFIC_ROLES",
            scope_value="SUPER_ADMIN"
        ))
    else:
        db.add(DocumentAudience(
            document_id=doc.id,
            scope_type="ENTIRE_INSTITUTION",
            scope_value=None
        ))

    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="DOCUMENT_UPLOAD",
        target_entity="InstitutionalDocument",
        target_id=doc.id,
        change_summary=f"Uploaded '{doc.file_name}' ({file_size} bytes). Extracted {len(extraction_res.contents)} blocks and {extraction_res.tables_found} tables.",
        actor_user_id=current_user.id
    )

    db.commit()
    db.refresh(doc)
    return _serialize_doc_review(doc)


@router.get("/", response_model=List[DocumentListItemOut])
def list_documents(
    status_filter: Optional[str] = Query(None),
    category_filter: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    batch: Optional[str] = Query(None),
    programme: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    is_admin = "SUPER_ADMIN" in user_roles

    query = db.query(InstitutionalDocument).filter(InstitutionalDocument.is_deleted == False)

    if not is_admin:
        query = query.filter(
            InstitutionalDocument.status == "PUBLISHED",
            InstitutionalDocument.is_current_published == True
        )

    if status_filter and is_admin:
        query = query.filter(InstitutionalDocument.status == status_filter)

    if category_filter:
        query = query.filter(InstitutionalDocument.category == category_filter)

    if academic_year:
        query = query.filter(InstitutionalDocument.academic_year == academic_year)

    if batch:
        query = query.filter(InstitutionalDocument.batch == batch)

    if programme:
        query = query.filter(InstitutionalDocument.programme == programme)

    if semester:
        query = query.filter(InstitutionalDocument.semester == semester)

    if branch:
        query = query.filter(InstitutionalDocument.branch == branch)

    docs = query.order_by(InstitutionalDocument.created_at.desc()).all()
    out = []

    for d in docs:
        if not is_admin and not audience_service.can_user_access_document(current_user, d):
            continue
        audiences = [
            AudienceScopeInput(scopeType=a.scope_type, scopeValue=a.scope_value)
            for a in d.audiences
        ]
        out.append(
            DocumentListItemOut(
                id=d.id,
                title=d.title,
                fileName=d.file_name,
                fileExtension=d.file_extension,
                fileSizeBytes=d.file_size_bytes,
                category=d.category,
                suggestedCategory=d.suggested_category,
                status=d.status,
                academicYear=d.academic_year,
                semester=d.semester,
                branch=d.branch,
                programme=d.programme,
                batch=d.batch,
                currentVersionNo=d.current_version_no,
                isCurrentPublished=d.is_current_published,
                uploadedAt=d.created_at.isoformat(),
                publishedAt=d.published_at.isoformat() if d.published_at else None,
                audiences=audiences,
                is_demo=d.is_demo
            )
        )

    return out


@router.get("/{doc_id}", response_model=DocumentReviewOut)
def get_document_for_review(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(InstitutionalDocument).filter(
        InstitutionalDocument.id == doc_id,
        InstitutionalDocument.is_deleted == False
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    if doc.is_deleted or doc.status == "RESTRICTED_CONFIDENTIAL" or doc.category == "INTERNAL_MARKS":
        if "SUPER_ADMIN" not in user_roles:
            raise HTTPException(status_code=403, detail="Forbidden: Restricted confidential academic record.")

    if "SUPER_ADMIN" not in user_roles and not audience_service.can_user_access_document(current_user, doc):
        raise HTTPException(status_code=403, detail="Document audience restricted.")

    return _serialize_doc_review(doc)


@router.get("/{doc_id}/reconcile-marks", response_model=MarksReconciliationOut)
def reconcile_internal_marks(
    doc_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Extracts and demonstrates reconciliation preview of confidential student marks
    against registered student records without modifying student seed data.
    """
    doc = db.query(InstitutionalDocument).filter(InstitutionalDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    seen_enrollments = set()
    duplicate_enrollments = set()
    extracted_records = []

    for t in doc.extracted_tables:
        headers = [str(h).replace("\n", " ").strip().lower() for h in (t.headers or [])]
        enroll_col = next((idx for idx, h in enumerate(headers) if "enrollment" in h), None)
        name_col = next((idx for idx, h in enumerate(headers) if "name" in h), None)

        if enroll_col is not None:
            for row in (t.rows or []):
                if len(row) > enroll_col:
                    raw_enroll = str(row[enroll_col]).replace("\n", "").strip()
                    m = re.search(r'(BT[A-Z0-9]{2}24[A-Z0-9]+)', raw_enroll)
                    if m:
                        enroll_clean = m.group(1)
                        name_raw = str(row[name_col]).strip() if (name_col is not None and len(row) > name_col) else "Unknown"
                        if enroll_clean in seen_enrollments:
                            duplicate_enrollments.add(enroll_clean)
                        seen_enrollments.add(enroll_clean)
                        extracted_records.append((enroll_clean, name_raw, t.page_number or 1, len(row)))

    # Match against User table in PostgreSQL
    matched_users = {
        u.roll_number: u
        for u in db.query(User).filter(User.roll_number.in_(seen_enrollments)).all()
    } if seen_enrollments else {}

    matched_count = 0
    unmatched_count = 0
    reconciled_items = []

    for enroll, sname, pno, col_count in extracted_records:
        if enroll in duplicate_enrollments:
            status_str = "DUPLICATE"
        elif enroll in matched_users:
            status_str = "MATCHED"
            matched_count += 1
        else:
            status_str = "UNMATCHED"
            unmatched_count += 1

        u_match = matched_users.get(enroll)
        reconciled_items.append(
            MarksReconciliationRecord(
                enrollmentNumber=enroll,
                studentName=sname,
                matchStatus=status_str,
                matchedUserId=u_match.id if u_match else None,
                matchedUserName=u_match.full_name if u_match else None,
                pageNumber=pno,
                columnsCount=col_count
            )
        )

    return MarksReconciliationOut(
        documentId=doc.id,
        documentTitle=doc.title,
        totalRecords=len(reconciled_items),
        matchedCount=matched_count,
        unmatchedCount=unmatched_count,
        duplicateCount=len(duplicate_enrollments),
        records=reconciled_items,
        notice="Confidential student records extracted. Explicit Super Admin approval is required before student identity association."
    )


@router.put("/{doc_id}/metadata", response_model=DocumentReviewOut)
def update_document_metadata(
    doc_id: str,
    payload: DocumentUpdateMetadata,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(InstitutionalDocument).filter(InstitutionalDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    changes = []
    if payload.title is not None and payload.title != doc.title:
        changes.append(f"title: '{doc.title}' -> '{payload.title}'")
        doc.title = payload.title
    if payload.category is not None and payload.category != doc.category:
        changes.append(f"category: '{doc.category}' -> '{payload.category}'")
        doc.category = payload.category
    if payload.academicYear is not None:
        doc.academic_year = payload.academicYear
    if payload.semester is not None:
        doc.semester = payload.semester
    if payload.branch is not None:
        doc.branch = payload.branch
    if payload.programme is not None:
        doc.programme = payload.programme
    if payload.batch is not None:
        doc.batch = payload.batch
    if payload.issuingAuthority is not None:
        doc.issuing_authority = payload.issuingAuthority
    if payload.status is not None:
        doc.status = payload.status

    if payload.audiences is not None:
        db.query(DocumentAudience).filter(DocumentAudience.document_id == doc.id).delete()
        for aud in payload.audiences:
            db.add(DocumentAudience(
                document_id=doc.id,
                scope_type=aud.scopeType,
                scope_value=aud.scopeValue
            ))
        changes.append("updated target audience rules")

    if doc.status == "NEEDS_REVIEW" and payload.status is None:
        doc.status = "READY_TO_PUBLISH"

    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="DOCUMENT_METADATA_UPDATE",
        target_entity="InstitutionalDocument",
        target_id=doc.id,
        change_summary="; ".join(changes) if changes else "Saved document metadata.",
        actor_user_id=current_user.id
    )

    db.commit()
    db.refresh(doc)
    return _serialize_doc_review(doc)


@router.post("/{doc_id}/publish", response_model=DocumentReviewOut)
def publish_document(
    doc_id: str,
    payload: DocumentPublishRequest,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(InstitutionalDocument).filter(InstitutionalDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if doc.category == "INTERNAL_MARKS":
        raise HTTPException(
            status_code=400,
            detail="Publishing raw confidential internal marks to general audiences is prohibited. Use the marks import reconciliation workflow."
        )

    if payload.isAuthoritative:
        prev_docs = db.query(InstitutionalDocument).filter(
            InstitutionalDocument.id != doc.id,
            InstitutionalDocument.category == doc.category,
            InstitutionalDocument.academic_year == doc.academic_year,
            InstitutionalDocument.branch == doc.branch,
            InstitutionalDocument.semester == doc.semester,
            InstitutionalDocument.is_current_published == True
        ).all()
        for p in prev_docs:
            p.is_current_published = False
            p.status = "SUPERSEDED"
            db.add(DocumentPublicationHistory(
                document_id=p.id,
                action="SUPERSEDED",
                actor_user_id=current_user.id,
                note=f"Superseded by authoritative document '{doc.title}' (v{doc.current_version_no})"
            ))

    doc.status = "PUBLISHED"
    doc.is_current_published = True
    doc.published_at = datetime.now(timezone.utc)
    doc.published_by_user_id = current_user.id

    if payload.audiences is not None:
        db.query(DocumentAudience).filter(DocumentAudience.document_id == doc.id).delete()
        for aud in payload.audiences:
            db.add(DocumentAudience(
                document_id=doc.id,
                scope_type=aud.scopeType,
                scope_value=aud.scopeValue
            ))

    db.add(DocumentPublicationHistory(
        document_id=doc.id,
        action="PUBLISHED",
        actor_user_id=current_user.id,
        note=payload.changeSummary or "Document published as authoritative."
    ))

    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="DOCUMENT_PUBLISH",
        target_entity="InstitutionalDocument",
        target_id=doc.id,
        change_summary=f"Published '{doc.title}' as authoritative current version {doc.current_version_no}.",
        actor_user_id=current_user.id
    )

    db.commit()
    db.refresh(doc)
    return _serialize_doc_review(doc)


@router.post("/{doc_id}/archive")
def archive_document(
    doc_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(InstitutionalDocument).filter(InstitutionalDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc.status = "ARCHIVED"
    doc.is_current_published = False

    db.add(DocumentPublicationHistory(
        document_id=doc.id,
        action="ARCHIVED",
        actor_user_id=current_user.id,
        note="Archived by Super Admin."
    ))

    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role="SUPER_ADMIN",
        action="DOCUMENT_ARCHIVE",
        target_entity="InstitutionalDocument",
        target_id=doc.id,
        change_summary=f"Archived document '{doc.title}'.",
        actor_user_id=current_user.id
    )

    db.commit()
    return {"message": "Document archived successfully."}


@router.get("/{doc_id}/download")
def download_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(InstitutionalDocument).filter(InstitutionalDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    if doc.is_deleted or doc.status == "RESTRICTED_CONFIDENTIAL" or doc.category == "INTERNAL_MARKS":
        if "SUPER_ADMIN" not in user_roles:
            raise HTTPException(status_code=403, detail="Forbidden: Restricted confidential academic record.")

    if "SUPER_ADMIN" not in user_roles and not audience_service.can_user_access_document(current_user, doc):
        raise HTTPException(status_code=403, detail="Forbidden: You are not authorized to download this file.")

    verified_path = storage_service.get_file_path(doc.file_path)
    return FileResponse(
        path=verified_path,
        filename=doc.file_name,
        media_type=doc.mime_type
    )
