# PocketUni — Module 1 Acceptance Audit Checklist

## 1. Core Architecture & Database
- [x] **PostgreSQL 18 Local Setup:** Verified connecting to `pocketuni` on `localhost:5432`.
- [x] **Driver:** `psycopg` 3 (`postgresql+psycopg`) operational.
- [x] **Safe Password Parsing:** Trailing `#` supported without truncation or URL corruption.
- [x] **Password Protection:** Passwords masked in logs, tests, and documentation.
- [x] **SQLite Elimination:** SQLite is NOT silently selected in runtime mode.
- [x] **Alembic Synchronized:** Uses the same engine and config as FastAPI.
- [x] **Database Tables:** All 50 required tables + `alembic_version` created.
- [x] **Database Health Check:** `GET /api/health` reports status, engine driver, database name, and PostgreSQL version.

## 2. Institutional Seeding & Data Integrity
- [x] **Super Admin Account:** Seeded `utsavkumawat05@gmail.com` with role `SUPER_ADMIN`.
- [x] **Faculty Directory:** 22 verified faculty members of MITS Centre for Artificial Intelligence seeded with actual designations and research interests.
- [x] **Mentor Role:** Dr. Mausam Chouksey seeded with active student mentor role.
- [x] **Synthetic Students:** 4 demo students seeded with `is_demo = True` and `DEMO-` prefix.
- [x] **Zero Real Student Seed Mixing:** Real student records from internal marks files are strictly isolated from demo fixtures.

## 3. Real Academic Document Ingestion
- [x] **Reference Documents:** All 9 supplied MITS CAI PDFs placed in `data/seed/incoming/`.
- [x] **16 Standard Categories:** Enforced across backend classification and frontend review modal.
- [x] **Induction Notice:** Extracted schedule, venues, and orientation blocks.
- [x] **Scheme of Study:** Extracted course codes (250311, etc.), credits, and L-T-P distribution.
- [x] **Syllabus:** Extracted units, learning objectives, and reference textbooks.
- [x] **Timetable OCR:** Scanned timetables processed via PyMuPDF + Tesseract OCR (5.5.0).
- [x] **Confidential Marks:** Minor 2 marks document classified as `INTERNAL_MARKS`, restricted to Super Admin, barred from general publication, with isolated marks reconciliation endpoint.
- [x] **Certifications:** Extracted professional certification course lists and credit policies.

## 4. Frontend Experience & Design
- [x] **Existing User Journeys Preserved:** Chat, Application Agent, Applications List, Application Detail, Student Profile, Faculty Profile, Faculty Directory, and Student Preview modal retained.
- [x] **Visual Refinement:** Ink navy, Slate blue, Warm stone, Paper, and Sage design tokens implemented.
- [x] **Super Admin UI:** Seamlessly integrated into PocketUni sidebar and navbar.
- [x] **Document Review Modal:** Supports metadata editing, audience assignment, and confidential marks reconciliation preview.
- [x] **Frontend Build:** `npm run build` succeeds with 0 TypeScript/Vite compilation errors.

## 5. Automated Test Suite
- [x] **17 of 17 Tests Passed:** All automated tests in `backend/tests/test_backend.py` passing on PostgreSQL 18.
- [x] **Module Boundary Respected:** Zero Module 2 implementation (no Gemini API, no embeddings, no pgvector, no RAG).
