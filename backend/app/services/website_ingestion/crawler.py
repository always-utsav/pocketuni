import time
import logging
import urllib.parse
from typing import Dict, Any, List, Set, Optional
import httpx
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.services.website_ingestion.source_registry import OFFICIAL_MITS_DOMAINS
from backend.app.services.website_ingestion.html_extractor import html_extractor
from backend.app.services.website_ingestion.duplicate_detector import compute_content_hash
from backend.app.models.website import InstitutionalSource, SourcePage, CrawlRun, ExtractedWebDocument

logger = logging.getLogger("pocketuni.crawler")


class PoliteCrawler:

    def __init__(self, rate_limit_delay: float = 0.5, timeout: float = 12.0):
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.headers = {
            "User-Agent": "PocketUni-AcademicBot/1.0 (+https://web.mitsgwalior.in/)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def is_safe_url(self, url: str) -> bool:
        """
        SSRF defense: Verifies that the URL belongs strictly to authorized official MITS domains
        and does not target internal / loopback addresses.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return False

            host = (parsed.hostname or "").lower()
            if not host:
                return False

            # Block private IP ranges and loopback
            if host in ["localhost", "127.0.0.1", "0.0.0.0", "::1"] or host.startswith(("10.", "192.168.", "172.")):
                return False

            # Must match allowed institutional domains
            return any(host == d or host.endswith(f".{d}") for d in OFFICIAL_MITS_DOMAINS)
        except Exception:
            return False

    async def crawl_source(
        self,
        db: Session,
        source: InstitutionalSource,
        max_pages: int = 15
    ) -> Dict[str, Any]:
        """
        Crawls the designated institutional source within polite boundaries.
        Stores pages, extracted text, and document links in PostgreSQL 18.
        """
        run = CrawlRun(
            source_id=source.id,
            status="RUNNING",
            started_at=datetime.now(timezone.utc)
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        visited: Set[str] = set()
        to_visit: List[Tuple[str, int]] = [(source.base_url, 0)]
        pages_crawled = 0
        pdfs_found = 0
        errors = 0

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
            while to_visit and pages_crawled < max_pages:
                current_url, depth = to_visit.pop(0)

                # Normalize URL
                current_url = current_url.split("#")[0]
                if current_url in visited or not self.is_safe_url(current_url):
                    continue

                visited.add(current_url)

                try:
                    logger.info(f"Crawling ({depth}/{source.crawl_depth}): {current_url}")
                    resp = await client.get(current_url)
                    time.sleep(self.rate_limit_delay)

                    if resp.status_code != 200:
                        logger.warning(f"Failed to fetch {current_url}: status {resp.status_code}")
                        errors += 1
                        continue

                    content_type = resp.headers.get("content-type", "")
                    if "text/html" not in content_type:
                        continue

                    # Extract HTML Content
                    extracted = html_extractor.extract(current_url, resp.text)
                    content_hash = compute_content_hash(extracted["extracted_text"])

                    # Save / Update SourcePage in PostgreSQL
                    page = db.query(SourcePage).filter(SourcePage.url == current_url).first()
                    now = datetime.now(timezone.utc)

                    if not page:
                        page = SourcePage(
                            source_id=source.id,
                            url=current_url,
                            canonical_url=extracted["canonical_url"],
                            title=extracted["title"] or current_url,
                            page_type=source.category,
                            department_name="Centre for Artificial Intelligence" if "cai" in current_url.lower() or "artificial" in current_url.lower() else "MITS General",
                            content_hash=content_hash,
                            http_status=resp.status_code,
                            raw_html=resp.text[:50000],  # snapshot first 50KB
                            extracted_text=extracted["extracted_text"],
                            metadata_json={
                                "headings": extracted["headings"],
                                "tables": extracted["tables"],
                                "meta_description": extracted["meta_description"]
                            },
                            version_no=1,
                            is_superseded=False,
                            retrieved_at=now,
                            last_crawled_at=now
                        )
                        db.add(page)
                        db.flush()
                    else:
                        # Check if content has evolved
                        if page.content_hash != content_hash:
                            page.version_no += 1
                            page.content_hash = content_hash
                            page.extracted_text = extracted["extracted_text"]
                            page.metadata_json = {
                                "headings": extracted["headings"],
                                "tables": extracted["tables"],
                                "meta_description": extracted["meta_description"]
                            }
                        page.last_crawled_at = now
                        page.http_status = resp.status_code

                    # Record extracted PDFs
                    for doc in extracted["pdf_documents"]:
                        existing_doc = db.query(ExtractedWebDocument).filter(
                            ExtractedWebDocument.source_page_id == page.id,
                            ExtractedWebDocument.file_url == doc["url"]
                        ).first()
                        if not existing_doc:
                            db.add(ExtractedWebDocument(
                                source_page_id=page.id,
                                file_url=doc["url"],
                                title=doc["title"][:490],
                                doc_type=doc["doc_type"]
                            ))
                            pdfs_found += 1

                    pages_crawled += 1

                    # Add new links to queue if within crawl depth
                    if depth < source.crawl_depth:
                        for link in extracted["discovered_links"]:
                            if link not in visited and self.is_safe_url(link):
                                to_visit.append((link, depth + 1))

                except Exception as e:
                    logger.error(f"Error crawling {current_url}: {e}")
                    errors += 1

        run.status = "COMPLETED" if errors == 0 else "PARTIAL"
        run.completed_at = datetime.now(timezone.utc)
        run.pages_discovered = len(visited) + len(to_visit)
        run.pages_crawled = pages_crawled
        run.pdfs_found = pdfs_found
        run.error_count = errors
        run.summary_json = {
            "visited_count": len(visited),
            "errors": errors,
            "pdfs": pdfs_found
        }

        source.last_crawled_at = datetime.now(timezone.utc)
        if pages_crawled > 0:
            source.last_success_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "source_id": source.id,
            "source_name": source.name,
            "status": run.status,
            "pages_crawled": pages_crawled,
            "pdfs_found": pdfs_found,
            "errors": errors
        }


polite_crawler = PoliteCrawler()
