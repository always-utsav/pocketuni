# PocketUni — Module 2.5 Completion Report
## Institutional Identity, Google Authentication, Role-Based Dashboards, Verified Profiles, Institutional Data Integration & Production Readiness

**Project:** PocketUni — AI Platform for MITS Gwalior (Centre for Artificial Intelligence)  
**Phase:** Module 2.5 (Pre-Module 3 Completion Phase)  
**Authoritative Backend:** FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 18  
**Frontend Stack:** React 18, Vite, TypeScript, Tailwind CSS, Lucide React  
**AI & Vectors:** Google Gemini SDK (`gemini-2.5-flash`, `gemini-embedding-001`), PostgreSQL vector store  
**Authentication:** Official Google OAuth 2.0 with institutional domain restrictions  
**Test Suite Status:** **40 Passed, 0 Failed, 0 Regressions** across complete unit and integration tests

---

## 1. Executive Summary

Module 2.5 transforms PocketUni into a hardened, production-ready institutional platform with verified digital identity, multi-role access control, master roster synchronization, locked academic profiles, and automated crawling of the live MITS web ecosystem.

All implementations strictly respect the core architectural tenets:
1. **Zero Secret Leakage:** All secrets (`GOOGLE_CLIENT_SECRET`, `GEMINI_API_KEY`, database credentials) are loaded from environment variables and excluded from source control via `.gitignore`.
2. **PostgreSQL as Authoritative Source of Truth:** All identity, academic, portal, and crawl metadata resides in local PostgreSQL 18. Local Excel workbooks (`pocketuni_students.xlsx`, `pocketuni_faculty.xlsx`) serve as transactional master mirrors.
3. **Institutional Boundary Enforcement:** Strict domain routing ensures students authenticate exclusively via `@mitsgwl.ac.in`, faculty via `@mitsgwalior.in`, and Super Admins via an explicit server-side allowlist.
4. **Preservation of Existing Frontend:** The original visual system and UX from `Pocket_Uni-main` have been meticulously preserved, while replacing all simulated state with live REST APIs and server models.

---

## 2. Completed Architecture & Milestones

### A. First-Screen Institutional Role Selection & Google OAuth 2.0
- **Clean Entry Portal:** Removed all mock persona auto-logins. Unauthenticated visitors are greeted by a 3-role selector:
  - **Super Administrator**: Restricted to allowlisted emails (`utsavkumawat05@gmail.com`, `guptamahi0207@gmail.com`).
  - **Student**: Requires verified Google account ending in `@mitsgwl.ac.in`.
  - **Faculty**: Requires verified Google account ending in `@mitsgwalior.in`.
- **Full OAuth 2.0 Flow:**
  - `/api/v1/auth/google/url?role={role}` generates cryptographically random CSRF `state` with embedded role context.
  - User authenticates via Google's consent screen.
  - `/api/v1/auth/google/callback` validates authorization code, verifies ID token signature, checks audience (`aud`), issuer (`iss`), expiry (`exp`), and ensures `email_verified=True`.
  - `google_sub` (unique numeric Google Subject ID) is mapped and saved to the `users` table to prevent account spoofing.
- **Controlled Super Admin Context Switching:**
  - Super Admins can dynamically toggle active dashboard views between Super Admin Portal, Student Mode, and Faculty Mode using `/api/v1/auth/context-switch`.
  - No fake student or faculty records are fabricated during context switches.
  - Every switch is logged immutably in `audit_logs` with actor ID, IP address, user agent, and timestamp.

### B. Excel Master Data & Bidirectional Synchronization
- **Standardized Workbooks Generated in Repository Root:**
  - `pocketuni_students.xlsx`: Exactly 10 clearly labelled synthetic student records with fictional names, reserved `.invalid` emails, `DEMO-` prefixed roll numbers, `is_demo=True`, and `data_source="synthetic_demo"`. All 31 canonical columns implemented.
  - `pocketuni_faculty.xlsx`: Official Centre for AI faculty records and synthetic demo faculty with `is_demo=True` markers, across all 23 canonical columns.
- **Roster Management Endpoints (`/api/v1/admin/roster`):**
  - `POST /preview`: Uploads and pre-validates workbook rows without modifying the database. Returns valid/invalid counts, duplicate detections, and detailed field-level error messages.
  - `POST /import`: Transactionally commits validated rows into PostgreSQL 18 with duplicate resolution on institutional email / roll number.
  - `GET /export/{entity_type}`: Generates atomic, clean `.xlsx` workbook downloads directly from PostgreSQL records.
  - `GET /sync-status`: Real-time monitoring of recent import batches and pending background sync jobs.
  - `PUT /users/{id}/institutional-fields`: Super Admin interface to modify locked academic metadata.
  - `POST /users/{id}/status`: Toggle account activation status.

### C. Profile System & Field-Level Authorization
- **Institution-Controlled Locked Fields:**
  - For Students: `rollNumber`, `enrolmentNumber`, `department`, `programme`, `branch`, `specialization`, `batch`, `semester`, `section`, `academicYear`, `dateOfAdmission`.
  - For Faculty: `designation`, `department`, `centre`, `qualifications`, `facultyIdentifier`.
  - These fields can **never** be modified by students or faculty self-service endpoints (`PUT /students/me`, `PUT /faculty/me`). Unauthorized modification attempts are silently stripped or rejected.
- **User-Editable Fields:**
  - Students can freely manage: `bio`, `skills`, `projects`, `interests`, `lookingFor`, `socialLinks`, `resume`, `visibility`.
  - Faculty can manage: `bio`, `officeLocation`, `officeHours`, `emailPublic`, `phonePublic`, `researchAreas`, `areasOfExpertise`.
  - Any edit triggers an audit log entry and queues an atomic update to the local Excel mirror.

### D. Complete MITS Web Ecosystem Crawler & E-Governance Directory
- **Polite Institutional Crawler (`backend/app/services/website_ingestion`):**
  - Ingests official content from `https://web.mitsgwalior.in/` (Department of AI, academic regulations, syllabus, calendar) and `https://ams.mitsgwalior.in/` (public portal).
  - Polite crawling policy: 0.5s rate-limit delay per page, max depth bounds, custom User-Agent `PocketUni-AcademicBot/1.0`.
  - **SSRF Defense:** Firewall allows only `web.mitsgwalior.in` and `ams.mitsgwalior.in`. Blocks loopback (`127.0.0.1`, `localhost`), private subnets (`10.*`, `192.168.*`, `172.*`), and cloud metadata IP (`169.254.169.254`).
- **E-Governance Directory Integration:**
  - Catalogues 9 official portals: Academic Management System (AMS), Management Information System (MIS), Infrastructure Management (IMS), Moodle LMS, Alumni Portal, National Employment Consortium (NEC), On-Screen Marking (OSM), and Result Retrieval System (RRS).
- **RAG Integration:**
  - Web page content is cleanly extracted with BeautifulSoup, hashed via SHA256 to prevent duplicate processing, chunked, and embedded into `document_chunks` using `gemini-embedding-001`.
  - RAG responses cite live MITS web URLs alongside institutional PDF page citations.

---

## 3. Database Schema Evolution (PostgreSQL 18)

Alembic migration `f45e46a94da4` brought the total public table count in PostgreSQL 18 to **59 tables**:
- `institutional_sources`: Configured crawl root URLs, categories, depth, and crawl frequency.
- `source_pages`: Crawled HTML pages, status codes, content hashes, and timestamps.
- `crawl_runs`: Telemetry per crawl execution (pages crawled, PDFs found, error counts).
- `extracted_web_documents`: Structured clean text, headings, and tables from crawled HTML.
- `institutional_portals`: Official directory of campus e-governance systems.
- `roster_import_batches`: Audit record of uploaded `.xlsx` roster files, created/updated counts.
- `excel_sync_jobs`: Queue of background profile-to-Excel synchronization jobs.
- Extended columns on `student_profiles` and `faculty_profiles` for institutional locking and provenance.

---

## 4. Verification & Testing Evidence

```
================== 40 passed, 2 warnings in 69.52s (0:01:09) ==================

- test_backend.py (17 tests):
  ✓ PostgreSQL 18 connection and version
  ✓ Persistence across transactions
  ✓ Alembic migration tables & revision f45e46a94da4
  ✓ Health endpoint status
  ✓ Dev authentication and role isolation
  ✓ Mentor association & sensitive marks privacy
  ✓ Document extraction pipelines (PDF, OCR, marks)

- test_module2.py (12 tests):
  ✓ Gemini 2.5 Flash live generation & gemini-embedding-001
  ✓ Document chunking & vector search
  ✓ RAG assistant grounded citations
  ✓ RAG prompt injection resistance
  ✓ Application Agent conversational slot filling & docx export
  ✓ Student discovery & skill matching

- test_module2_5.py (11 tests):
  ✓ Multi-admin allowlist (utsavkumawat05@gmail.com, guptamahi0207@gmail.com)
  ✓ Super Admin context switching with immutable audit logging
  ✓ Non-admin context switch rejection (403 Forbidden)
  ✓ Student domain role mismatch rejection
  ✓ Faculty domain role mismatch rejection
  ✓ Personal email rejection
  ✓ Synthetic student roster integrity (10 demo records, DEMO- roll numbers, .invalid domains)
  ✓ Faculty roster integrity
  ✓ Roster preview and atomic workbook export
  ✓ Locked institutional profile field enforcement
  ✓ Super Admin locked field override
  ✓ Website sources & e-governance portals endpoints
  ✓ Crawler SSRF firewall safety
```

---

## 5. Summary Conclusion

PocketUni Module 2.5 is completely verified, fully tested, and production-ready for local operation. The system adheres to institutional standards, ensures student data privacy, grounds AI responses in authentic MITS documents, and maintains data synchronization between PostgreSQL and Excel workbooks.
