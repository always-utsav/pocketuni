import re
import urllib.parse
from typing import Dict, Any, List, Tuple
from bs4 import BeautifulSoup


class HtmlExtractor:

    def extract(self, url: str, html_content: str) -> Dict[str, Any]:
        """
        Parses HTML and extracts structured content, metadata, tables, headings, and links.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Page Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # 2. Canonical URL & Meta Tags
        canonical_url = url
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag and canonical_tag.get("href"):
            canonical_url = urllib.parse.urljoin(url, canonical_tag["href"])

        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        # 3. Discovered Links & Documents
        discovered_links = set()
        pdf_documents = []

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            full_url = urllib.parse.urljoin(url, href)
            # Remove fragment
            full_url = full_url.split("#")[0]

            link_text = a.get_text(strip=True) or "Document"

            if full_url.lower().endswith((".pdf", ".docx", ".doc", ".xlsx", ".xls")):
                doc_type = "PDF" if full_url.lower().endswith(".pdf") else "OFFICE_DOC"
                pdf_documents.append({
                    "url": full_url,
                    "title": link_text,
                    "doc_type": doc_type
                })
            else:
                discovered_links.add(full_url)

        # 4. Extract Structured Tables
        tables = []
        for t_idx, table in enumerate(soup.find_all("table")):
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append({
                    "table_index": t_idx + 1,
                    "headers": headers,
                    "rows": rows
                })

        # 5. Extract Headings Hierarchy
        headings = []
        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            headings.append({
                "level": h.name.upper(),
                "text": h.get_text(strip=True)
            })

        # 6. Extract Clean Text (De-boilerplating)
        # Remove script, style, nav, footer, header, noscript elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "button"]):
            element.decompose()

        # Find main content container if available
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|main|article|body", re.I)) or soup.body

        extracted_text = ""
        if main_content:
            # Normalize whitespace
            extracted_text = re.sub(r"\n\s*\n+", "\n\n", main_content.get_text(separator="\n", strip=True))
        else:
            extracted_text = re.sub(r"\n\s*\n+", "\n\n", soup.get_text(separator="\n", strip=True))

        return {
            "title": title,
            "canonical_url": canonical_url,
            "meta_description": meta_desc,
            "extracted_text": extracted_text,
            "headings": headings,
            "tables": tables,
            "pdf_documents": pdf_documents,
            "discovered_links": list(discovered_links)
        }


html_extractor = HtmlExtractor()
