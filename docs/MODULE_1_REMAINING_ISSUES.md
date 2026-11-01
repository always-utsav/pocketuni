# PocketUni — Module 1 Remaining Issues & Status Breakdown

| Item | Status | Verification Detail |
|---|---|---|
| PostgreSQL 18 Local Setup | **IMPLEMENTED & TESTED** | Verified running on `localhost:5432/pocketuni`. Connecting via `postgresql+psycopg` with URL creation handling trailing `#` in passwords. |
| 50-Table Schema Migration | **IMPLEMENTED & TESTED** | Alembic migration `1e5131ff1c7b` applied. 51 public tables verified in PostgreSQL. |
| SQLite Fallback Removal | **IMPLEMENTED & TESTED** | Fallback removed from runtime engine. Clear `OperationalError` raised if database is offline. |
| Dev Authentication & RBAC | **IMPLEMENTED & TESTED** | Local token issuing tested with Super Admin allowlist (`utsavkumawat05@gmail.com`) and student roles. |
| MITS CAI Document Extraction | **IMPLEMENTED & TESTED** | All 9 reference PDFs extracted, categorized across 16 categories, and stored with page-level text blocks. |
| Tesseract OCR Timetable Processing | **IMPLEMENTED & TESTED** | Tesseract 5.5.0 connected via PyMuPDF rendering to extract scanned timetables (`III Sem`, `V Sem`, `VII Sem`). |
| Internal Marks Confidentiality | **IMPLEMENTED & TESTED** | Minor 2 marks PDF classified as `INTERNAL_MARKS`, restricted to Super Admin, with isolated reconciliation endpoint. |
| Super Admin Review & Publishing | **IMPLEMENTED & TESTED** | Metadata editing, audience scoping, and audit logging tested end-to-end. |
| Frontend Design Tokens & UI Integration | **IMPLEMENTED & TESTED** | University palette (Ink navy, Slate blue, Warm stone, Paper, Sage, Terracotta) applied across landing page, sidebar, navbar, and admin view. Clean build (`npm run build`). |
| Google OAuth Production Credentials | **AWAITING CONFIGURATION** | Google Client ID/Secret not yet provided; controlled dev auth is active for local testing. |
| Production SMTP Email Dispatch | **AWAITING CONFIGURATION** | Notification records persisted to database; real SMTP transmission deferred to operational production setup. |
| Vector Embeddings & Gemini RAG | **DEFERRED TO MODULE 2** | By project specification, AI retrieval, pgvector, and Gemini API integration will commence exclusively in Module 2. |
