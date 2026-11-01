from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.core.permissions import get_current_user, require_super_admin
from backend.app.models.identity import User
from backend.app.models.website import InstitutionalSource, SourcePage, CrawlRun, ExtractedWebDocument, InstitutionalPortal
from backend.app.services.website_ingestion.ingestion_pipeline import website_ingestion_pipeline
from backend.app.services.website_ingestion.source_registry import OFFICIAL_MITS_DOMAINS
from backend.app.services.audit_service import log_audit_event

router = APIRouter()


class AddSourceRequest(BaseModel):
    name: str
    domain: str
    base_url: str
    category: str = "MITS_MAIN"
    crawl_depth: int = 2
    crawl_frequency_hours: int = 24
    description: Optional[str] = None


class CrawlTriggerRequest(BaseModel):
    source_id: Optional[str] = None
    max_pages: int = 10


@router.get("/sources")
def list_sources(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Lists registered institutional web sources with crawl status and telemetry."""
    sources = db.query(InstitutionalSource).all()
    if not sources:
        website_ingestion_pipeline.initialize_registry(db)
        sources = db.query(InstitutionalSource).all()

    return [
        {
            "id": s.id,
            "name": s.name,
            "domain": s.domain,
            "base_url": s.base_url,
            "category": s.category,
            "crawl_status": s.crawl_status,
            "crawl_depth": s.crawl_depth,
            "crawl_frequency_hours": s.crawl_frequency_hours,
            "last_crawled_at": s.last_crawled_at.isoformat() if s.last_crawled_at else None,
            "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
            "pages_count": len(s.pages),
            "description": s.description
        }
        for s in sources
    ]


@router.post("/sources")
def add_source(
    payload: AddSourceRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Allows Super Admin to register a new verified institutional source URL."""
    # SSRF verification: domain must belong to MITS ecosystem
    clean_domain = payload.domain.lower().strip()
    if not any(clean_domain == d or clean_domain.endswith(f".{d}") for d in OFFICIAL_MITS_DOMAINS):
        raise HTTPException(
            status_code=400,
            detail=f"Domain '{payload.domain}' is not in the authorized MITS ecosystem allowlist."
        )

    existing = db.query(InstitutionalSource).filter(InstitutionalSource.base_url == payload.base_url).first()
    if existing:
        raise HTTPException(status_code=400, detail="An institutional source with this base URL already exists.")

    src = InstitutionalSource(
        name=payload.name,
        domain=clean_domain,
        base_url=payload.base_url,
        category=payload.category,
        crawl_depth=payload.crawl_depth,
        crawl_frequency_hours=payload.crawl_frequency_hours,
        description=payload.description
    )
    db.add(src)
    db.commit()
    db.refresh(src)

    log_audit_event(
        db=db,
        actor_email=current_admin.email,
        actor_role="SUPER_ADMIN",
        action="ADD_INSTITUTIONAL_SOURCE",
        target_entity="InstitutionalSource",
        target_id=src.id,
        change_summary=f"Added institutional web source: {src.name} ({src.base_url})"
    )

    return {"message": "Institutional source registered successfully.", "source_id": src.id}


@router.post("/crawl")
async def trigger_crawl(
    payload: CrawlTriggerRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Triggers crawler execution across registered sources with RAG embedding updates."""
    result = await website_ingestion_pipeline.run_crawler_and_index(db, max_pages_per_source=payload.max_pages)
    return {
        "message": "Crawling and embedding cycle completed.",
        "results": result
    }


@router.get("/portals")
def list_portals(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Public directory of official MITS institutional portals and e-governance systems.
    Available to all authenticated users.
    """
    query = db.query(InstitutionalPortal)
    if category:
        query = query.filter(InstitutionalPortal.category == category.upper())

    portals = query.order_by(InstitutionalPortal.name.asc()).all()
    if not portals:
        website_ingestion_pipeline.initialize_registry(db)
        portals = db.query(InstitutionalPortal).order_by(InstitutionalPortal.name.asc()).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "officialUrl": p.official_url,
            "domain": p.domain,
            "purpose": p.purpose,
            "servicesDescription": p.services_description,
            "authRequired": p.auth_required,
            "integrationStatus": p.integration_status,
            "lastVerifiedAt": p.last_verified_at.isoformat() if p.last_verified_at else None
        }
        for p in portals
    ]


@router.get("/stats")
def get_crawler_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_super_admin)
):
    """Returns detailed crawling telemetry for Super Admin dashboard."""
    sources_count = db.query(InstitutionalSource).count()
    pages_count = db.query(SourcePage).count()
    docs_count = db.query(ExtractedWebDocument).count()
    runs = db.query(CrawlRun).order_by(CrawlRun.started_at.desc()).limit(10).all()

    return {
        "sources_count": sources_count,
        "pages_count": pages_count,
        "extracted_docs_count": docs_count,
        "recent_runs": [
            {
                "id": r.id,
                "source_id": r.source_id,
                "status": r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "pages_crawled": r.pages_crawled,
                "pdfs_found": r.pdfs_found,
                "error_count": r.error_count
            }
            for r in runs
        ]
    }
