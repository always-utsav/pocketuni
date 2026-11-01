import logging
import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.models.website import InstitutionalSource, SourcePage, InstitutionalPortal
from backend.app.models.document import InstitutionalDocument, DocumentChunk
from backend.app.services.website_ingestion.source_registry import (
    INITIAL_INSTITUTIONAL_SOURCES,
    OFFICIAL_PORTALS_CATALOGUE
)
from backend.app.services.website_ingestion.crawler import polite_crawler
from backend.app.services.gemini_service import gemini_service

logger = logging.getLogger("pocketuni.website_ingestion")


class WebsiteIngestionPipeline:

    def initialize_registry(self, db: Session) -> Dict[str, int]:
        """
        Seeds initial institutional sources and e-governance portals if not already present.
        """
        sources_added = 0
        portals_added = 0

        for src_data in INITIAL_INSTITUTIONAL_SOURCES:
            existing = db.query(InstitutionalSource).filter(InstitutionalSource.base_url == src_data["base_url"]).first()
            if not existing:
                src = InstitutionalSource(
                    name=src_data["name"],
                    domain=src_data["domain"],
                    base_url=src_data["base_url"],
                    category=src_data["category"],
                    crawl_depth=src_data["crawl_depth"],
                    crawl_frequency_hours=src_data["crawl_frequency_hours"],
                    auth_required=src_data["auth_required"],
                    allowed_patterns=src_data["allowed_patterns"],
                    excluded_patterns=src_data["excluded_patterns"],
                    description=src_data["description"]
                )
                db.add(src)
                sources_added += 1

        for portal_data in OFFICIAL_PORTALS_CATALOGUE:
            existing = db.query(InstitutionalPortal).filter(InstitutionalPortal.official_url == portal_data["official_url"]).first()
            if not existing:
                portal = InstitutionalPortal(
                    name=portal_data["name"],
                    category=portal_data["category"],
                    official_url=portal_data["official_url"],
                    domain=portal_data["domain"],
                    purpose=portal_data["purpose"],
                    services_description=portal_data["services_description"],
                    auth_required=portal_data["auth_required"],
                    contains_confidential_records=portal_data["contains_confidential_records"],
                    integration_status=portal_data["integration_status"],
                    last_verified_at=datetime.now(timezone.utc)
                )
                db.add(portal)
                portals_added += 1

        db.commit()
        logger.info(f"Initialized registry: {sources_added} sources, {portals_added} portals added.")
        return {"sources_added": sources_added, "portals_added": portals_added}

    async def run_crawler_and_index(self, db: Session, max_pages_per_source: int = 10) -> Dict[str, Any]:
        """
        Runs crawler across registered institutional sources, extracts pages,
        and generates vector embeddings for grounding RAG with live URLs.
        """
        self.initialize_registry(db)
        sources = db.query(InstitutionalSource).filter(InstitutionalSource.crawl_status == "ACTIVE").all()

        crawl_results = []
        total_chunks_created = 0

        # Create or find a virtual InstitutionalDocument to hold web chunks
        web_parent_doc = db.query(InstitutionalDocument).filter(
            InstitutionalDocument.file_name == "MITS_OFFICIAL_WEB_ECOSYSTEM.html"
        ).first()
        if not web_parent_doc:
            web_parent_doc = InstitutionalDocument(
                title="MITS Official Web Ecosystem & CAI Directory",
                file_name="MITS_OFFICIAL_WEB_ECOSYSTEM.html",
                file_path="https://web.mitsgwalior.in/",
                file_size_bytes=1024,
                mime_type="text/html",
                file_extension=".html",
                content_hash="web_ecosystem_root_hash",
                category="INSTITUTIONAL_WEBSITE",
                indexing_status="INDEXED",
                embedding_model="gemini-embedding-001"
            )
            db.add(web_parent_doc)
            db.commit()
            db.refresh(web_parent_doc)

        for src in sources:
            result = await polite_crawler.crawl_source(db, src, max_pages=max_pages_per_source)
            crawl_results.append(result)

        # Index crawled pages into PostgreSQL document_chunks for RAG
        pages = db.query(SourcePage).filter(SourcePage.is_superseded == False).all()

        for page in pages:
            text = (page.extracted_text or "").strip()
            if not text or len(text) < 100:
                continue

            # Check if page chunk already exists
            existing_chunk = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == web_parent_doc.id,
                DocumentChunk.chunk_text.like(f"%{page.url}%")
            ).first()
            if existing_chunk:
                continue

            # Slice page into manageable RAG chunks (~1000 chars)
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 60]
            current_chunk = f"Source: {page.title} ({page.url})\n\n"

            for para in paragraphs:
                if len(current_chunk) + len(para) > 1200:
                    try:
                        time.sleep(0.5)
                        embedding = gemini_service.embed_text(current_chunk)
                        chunk_record = DocumentChunk(
                            document_id=web_parent_doc.id,
                            version_id=str(web_parent_doc.current_version_no),
                            chunk_index=web_parent_doc.indexed_chunks_count + 1,
                            chunk_text=current_chunk,
                            token_count=len(current_chunk.split()),
                            source_page_number=1,
                            source_section=page.title[:250] if page.title else "Web Overview",
                            category="INSTITUTIONAL_WEBSITE",
                            publication_status="PUBLISHED",
                            is_current=True,
                            audience_metadata=[{"scope_type": "ALL", "source_url": page.url}],
                            embedding_model=gemini_service.embedding_model,
                            embedding_dimension=len(embedding),
                            embedding_json=embedding
                        )
                        db.add(chunk_record)
                        web_parent_doc.indexed_chunks_count += 1
                        total_chunks_created += 1
                        db.commit()
                    except Exception as emb_err:
                        logger.warning(f"Could not embed chunk for {page.url}: {emb_err}")
                    current_chunk = f"Source: {page.title} ({page.url})\n\n{para}\n\n"
                else:
                    current_chunk += f"{para}\n\n"

            if len(current_chunk) > 150:
                try:
                    time.sleep(0.5)
                    embedding = gemini_service.embed_text(current_chunk)
                    chunk_record = DocumentChunk(
                        document_id=web_parent_doc.id,
                        version_id=str(web_parent_doc.current_version_no),
                        chunk_index=web_parent_doc.indexed_chunks_count + 1,
                        chunk_text=current_chunk,
                        token_count=len(current_chunk.split()),
                        source_page_number=1,
                        source_section=page.title[:250] if page.title else "Web Overview",
                        category="INSTITUTIONAL_WEBSITE",
                        publication_status="PUBLISHED",
                        is_current=True,
                        audience_metadata=[{"scope_type": "ALL", "source_url": page.url}],
                        embedding_model=gemini_service.embedding_model,
                        embedding_dimension=len(embedding),
                        embedding_json=embedding
                    )
                    db.add(chunk_record)
                    web_parent_doc.indexed_chunks_count += 1
                    total_chunks_created += 1
                    db.commit()
                except Exception as emb_err:
                    logger.warning(f"Could not embed final chunk for {page.url}: {emb_err}")

        web_parent_doc.indexed_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "crawl_summary": crawl_results,
            "indexed_web_chunks": total_chunks_created,
            "total_web_chunks": web_parent_doc.indexed_chunks_count
        }


website_ingestion_pipeline = WebsiteIngestionPipeline()
