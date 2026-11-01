import os
import hashlib
from datetime import datetime, timezone
from backend.app.core.database import SessionLocal
from backend.app.models.identity import User
from backend.app.models.document import (
    InstitutionalDocument,
    DocumentVersion,
    DocumentAudience,
    DocumentExtractionJob,
    ExtractedDocumentContent,
    ExtractedTable,
    DocumentPublicationHistory
)
from backend.app.services.extraction_service import extraction_engine
from backend.app.services.classification_service import classification_service
from backend.app.services.rag_service import rag_service

def ingest_incoming_docs():
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "utsavkumawat05@gmail.com").first()
    admin_id = admin.id if admin else None

    incoming_dir = os.path.abspath("data/seed/incoming")
    if not os.path.exists(incoming_dir):
        print(f"Directory {incoming_dir} not found.")
        db.close()
        return

    files = [f for f in os.listdir(incoming_dir) if f.lower().endswith(".pdf")]
    print(f"Found {len(files)} PDFs in incoming directory.")

    for f in files:
        file_path = os.path.join(incoming_dir, f)
        with open(file_path, "rb") as fp:
            data = fp.read()
        file_hash = hashlib.sha256(data).hexdigest()

        # Check if already present
        existing = db.query(InstitutionalDocument).filter(
            InstitutionalDocument.content_hash == file_hash,
            InstitutionalDocument.is_deleted == False
        ).first()
        if existing and existing.indexing_status == "INDEXED":
            print(f"Skipping already indexed: {f}")
            continue

        print(f"\nIngesting: {f}...")
        ext_res = extraction_engine.extract(file_path, "application/pdf")
        clf = classification_service.classify_and_extract_metadata(
            title=f.replace(".pdf", ""),
            contents=ext_res.contents,
            tables=ext_res.tables,
            source_filename=f
        )

        category = clf.get("category", "OTHER")
        is_internal_marks = (category == "INTERNAL_MARKS")

        doc = existing or InstitutionalDocument(
            title=f.replace(".pdf", "").replace("_", " ").strip(),
            file_name=f,
            file_path=file_path,
            file_size_bytes=len(data),
            mime_type="application/pdf",
            file_extension=".pdf",
            content_hash=file_hash,
            category=category,
            suggested_category=category,
            academic_year=clf.get("academic_year") or "2026-27",
            semester=clf.get("semester"),
            programme=(clf.get("programme") or "B.Tech")[:100],
            branch=(clf.get("branch") or "Artificial Intelligence")[:100],
            batch=(clf.get("batch") or "")[:50] if clf.get("batch") else None,
            issuing_authority=(clf.get("issuing_institution") or "MITS Gwalior")[:255],
            status="NEEDS_REVIEW" if is_internal_marks else "PUBLISHED",
            is_current_published=not is_internal_marks,
            current_version_no=1,
            uploaded_by_user_id=admin_id,
            published_by_user_id=admin_id if not is_internal_marks else None,
            published_at=datetime.now(timezone.utc) if not is_internal_marks else None,
            is_demo=False
        )

        if not existing:
            db.add(doc)
            db.flush()

            # Version record
            db.add(DocumentVersion(
                document_id=doc.id,
                version_no=1,
                file_name=f,
                file_path=file_path,
                content_hash=file_hash,
                change_summary="Authoritative institutional ingestion"
            ))

            # Audience
            if is_internal_marks:
                db.add(DocumentAudience(document_id=doc.id, scope_type="SUPER_ADMIN", scope_value="Confidential Marks"))
            else:
                db.add(DocumentAudience(document_id=doc.id, scope_type="CENTRE_FOR_AI", scope_value=clf.get("branch") or "AI"))
                db.add(DocumentAudience(document_id=doc.id, scope_type="ENTIRE_INSTITUTION", scope_value="Campus"))

            # Contents
            for item in ext_res.contents:
                db.add(ExtractedDocumentContent(
                    document_id=doc.id,
                    page_number=item.get("page_number"),
                    heading=item.get("heading"),
                    content=item.get("content", ""),
                    content_type=item.get("content_type", "paragraph")
                ))

            # Tables
            for tbl in ext_res.tables:
                db.add(ExtractedTable(
                    document_id=doc.id,
                    page_number=tbl.get("page_number"),
                    sheet_name=tbl.get("sheet_name"),
                    table_index=tbl.get("table_index", 1),
                    headers=tbl.get("headers", []),
                    rows=tbl.get("rows", []),
                    row_count=tbl.get("row_count", 0)
                ))

            db.commit()

        # If published, index into RAG vector repository
        if doc.is_current_published and not is_internal_marks:
            print(f"Indexing into RAG: {doc.title} ({doc.category})...")
            rag_info = rag_service.index_document(db, doc.id)
            print(f"Successfully indexed {rag_info['chunks_count']} chunks for {doc.title}.")
        else:
            print(f"Excluded from general RAG: {doc.title} (Status: {doc.status}, Category: {doc.category})")

    db.close()
    print("\nDocument ingestion and RAG vector indexing completed successfully!")

if __name__ == "__main__":
    ingest_incoming_docs()
