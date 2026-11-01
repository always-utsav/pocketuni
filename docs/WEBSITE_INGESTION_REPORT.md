# Website Ingestion Architecture & Ingestion Report
## PocketUni — MITS Gwalior AI Platform

This document describes the web ingestion engine that crawls official MITS institutional websites and integrates live institutional web knowledge into the RAG vector repository.

---

## 1. Web Ingestion Pipeline Architecture

```
+-------------------------------------------------------------+
|                Configured Institutional Sources             |
|  - web.mitsgwalior.in (Main university portal & CAI pages)  |
|  - ams.mitsgwalior.in (Public portal landing & notices)     |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                  PoliteCrawler Engine                       |
|  - SSRF Verification (Restricted to allowlisted domains)    |
|  - Rate-limit Throttling (0.5s delay between requests)      |
|  - Max Depth Restriction (Depth <= 2)                       |
|  - Custom User-Agent: PocketUni-AcademicBot/1.0             |
+-------------------------------------------------------------+
                               | HTML Response
                               v
+-------------------------------------------------------------+
|                  html_extractor Service                     |
|  - BeautifulSoup semantic DOM parsing                       |
|  - Strip headers, navigation, footers, scripts, and ads     |
|  - Extract clean article text, page title, and headings     |
|  - Extract structured tables (HTML -> Markdown)             |
|  - Discover embedded PDF links and outgoing anchor URLs     |
+-------------------------------------------------------------+
                               | Clean Structured Text
                               v
+-------------------------------------------------------------+
|               duplicate_detector (SHA256)                   |
|  - Compute content hash of cleaned text                     |
|  - Check if source_pages already contains matching hash     |
|  - Skip unchanged pages to avoid duplicate vector chunks    |
+-------------------------------------------------------------+
                               | Unique Changed Page
                               v
+-------------------------------------------------------------+
|              Vector Chunking & RAG Embedding Pipeline       |
|  - Chunk semantic sections with title and source URL        |
|  - Generate 3072-dim embeddings via gemini-embedding-001    |
|  - Store into document_chunks with category="WEBSITE_PAGE"  |
+-------------------------------------------------------------+
```

---

## 2. Ingestion Telemetry & Seed Run Statistics

During the initial ingestion run, the polite crawler extracted and indexed authoritative institutional pages from the live MITS web ecosystem:

| Source Name | Root URL | Category | Status | Pages Crawled | Chunks Generated |
|---|---|---|:---:|:---:|:---:|
| **MITS Gwalior Main Website** | `https://web.mitsgwalior.in/` | `MITS_MAIN` | `COMPLETED` | 8 | 9 |
| **Centre for Artificial Intelligence** | `https://web.mitsgwalior.in/academics/centre-for-ai` | `CAI` | `COMPLETED` | 1 | 2 |
| **Academic Management System** | `https://ams.mitsgwalior.in/` | `AMS_PUBLIC` | `COMPLETED` | 1 | 1 |
| **Total Web Chunks Indexed** | — | — | — | **10** | **12** |

---

## 3. RAG Grounding & Live URL Citations

When a student or faculty member asks questions regarding university leadership, departmental history, or official schemes:
1. The vector search matches semantic text from `document_chunks`.
2. The RAG service inspects `audience_metadata` or chunk headers for `source_url`.
3. The response synthesized by `gemini-2.5-flash` includes both PDF citations and clickable live web links:
   ```markdown
   According to the Department of Artificial Intelligence profile [1]:
   The Centre for Artificial Intelligence at MITS Gwalior focuses on...
   
   Sources:
   [1] Centre for AI Overview — https://web.mitsgwalior.in/academics/centre-for-ai
   ```
