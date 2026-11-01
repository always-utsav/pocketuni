# PocketUni — Manual Setup & Implementation Status Checklist
**Project:** PocketUni  
**Module:** 1 of 3 (Foundation, Authentication, Database, Super Admin & Document Management)  
**Reference Institution:** Madhav Institute of Technology & Science (MITS), Gwalior  

---

## 1. Status Legend

* **IMPLEMENTED:** Fully engineered, verified in code, and active.
* **TESTED:** Covered by automated test suite (`pytest` passing 100%).
* **AWAITING CONFIGURATION:** Ready in code; requires local user credentials or optional local tools.
* **AWAITING VERIFICATION:** Stored with official source metadata; pending institutional administration sign-off.
* **DEFERRED TO MODULE 2:** Architecture and interfaces prepared; implementation scoped strictly for Module 2 (AI, Gemini, RAG retrieval).
* **DEFERRED TO MODULE 3:** Advanced scaling, deployment, multi-tenant packaging.

---

## 2. Comprehensive Status Matrix

| Subsystem / Feature | Status | Notes & Verification Details |
| :--- | :--- | :--- |
| **Existing Frontend Preservation** | **IMPLEMENTED & TESTED** | 100% of existing journeys preserved (`LandingPage`, `ChatView`, `ApplicationAgentChat`, `ApplicationListView`, `StudentProfileView`, `FacultyProfileView`, etc.). Builds cleanly with Vite. |
| **Refined Visual Design Tokens** | **IMPLEMENTED** | Palette applied: Ink Navy (`#202C39`), Slate Blue (`#536B7A`), Muted Terracotta (`#B56F4A`), Warm Stone (`#E8E2D8`), Paper (`#F7F6F2`), Sage (`#668477`). |
| **PostgreSQL Local Server Setup** | **IMPLEMENTED & TESTED** | PostgreSQL 18 is running locally on Windows (`localhost:5432/pocketuni`). `psycopg` 3 and SQLAlchemy URL object handling configured for passwords containing special characters (e.g. trailing `#`). Runtime SQLite fallback has been completely eliminated. |
| **SQLAlchemy 2 Schema (50 Tables)** | **IMPLEMENTED & TESTED** | Identity, Academic, Student, Faculty, Application, Communication, Document Management, Records, and Audit tables fully defined. |
| **Alembic Database Migrations** | **IMPLEMENTED & TESTED** | Migration script `20261031_0956_1e5131ff1c7b_initial_50_table_schema.py` generated and applied with zero errors. |
| **Seed Scripts & Synthetic Data** | **IMPLEMENTED & TESTED** | `seed.py` seeds initial Super Admin (`utsavkumawat05@gmail.com`), synthetic students (`DEMO-` prefix, `is_demo=True`), and CAI faculty. |
| **Super Admin Security Enforcement** | **IMPLEMENTED & TESTED** | Strict server-side allowlist (`SUPER_ADMIN_ALLOWLIST`). Privileged APIs rejected with 403 Forbidden for non-admins. |
| **Controlled Local Dev Auth** | **IMPLEMENTED & TESTED** | Pre-registered demo accounts generate valid JWT tokens with role verification. Disabled in production configuration. |
| **Official MITS Faculty Import** | **IMPLEMENTED & TESTED** | 22 Centre for AI faculty members imported from `web.mitsgwalior.in`. Dr. Mausam Chouksey prominently featured with verified publications and designated mentor tag. |
| **MITS Academic Calendar (2026–27)** | **IMPLEMENTED & TESTED** | Stored official milestone schedules, explicitly distinguishing 2nd/3rd year and final-year calendars. |
| **Local Filesystem Document Storage** | **IMPLEMENTED & TESTED** | Files stored securely in `storage/institutional_documents/` with SHA-256 hash digest, extension and MIME validation, and path traversal prevention. |
| **PDF Extraction Engine** | **IMPLEMENTED & TESTED** | `pdfplumber` + `pypdf` extraction of page numbers, headings, structured tables, and empty/scanned page detection. |
| **DOCX Extraction Engine** | **IMPLEMENTED & TESTED** | `python-docx` extraction preserving heading hierarchy, paragraphs, and multi-column tables. |
| **XLSX & CSV Extraction Engine** | **IMPLEMENTED & TESTED** | `openpyxl` and `pandas` extraction preserving sheet names, column headers, and structured record counts. |
| **OCR for Scanned Documents** | **IMPLEMENTED & TESTED** | PyMuPDF (2.0) and Tesseract OCR (5.5.0) installed and verified on Windows (`C:\Program Files\Tesseract-OCR\tesseract.exe`). Successfully extracts scanned timetable schedules (III Sem, V Sem, VII Sem). |
| **Super Admin Dashboard (15 Sections)** | **IMPLEMENTED & TESTED** | Complete interface with live metrics, upload forms, document review modal, audience selection, and audit views. |
| **Target Audience Governance** | **IMPLEMENTED & TESTED** | Server-side audience enforcement (`ENTIRE_INSTITUTION`, `CENTRE_FOR_AI`, `BRANCH`, `SEMESTER`, etc.). |
| **Authoritative Versioning** | **IMPLEMENTED & TESTED** | Publishing replaces superseded documents for the matching scope while retaining traceable history in `document_versions`. |
| **Strict Result Privacy** | **IMPLEMENTED & TESTED** | Students can only access their own results. Super Admin access audited. Marks datasets isolated from general public queries. |
| **Immutable Audit Logging** | **IMPLEMENTED & TESTED** | All uploads, logins, publications, and results queries automatically recorded in `audit_logs`. |
| **Centralised Frontend API Client** | **IMPLEMENTED & TESTED** | `src/services/apiClient.ts` coordinates communication between React frontend and FastAPI backend. |
| **Google OAuth Production Auth** | **AWAITING CONFIGURATION** | Integration points and token decode prepared; pending Google Cloud Client ID/Secret configuration. |
| **Gemini AI & Semantic RAG** | **DEFERRED TO MODULE 2** | Chunking models, embeddings, vector indexing, and Gemini API calls are strictly scoped for Module 2. |
| **Slot-Filling Application Agent** | **DEFERRED TO MODULE 2** | UI preserved; live Gemini conversational engine will be connected in Module 2. |
