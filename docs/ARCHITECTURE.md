# PocketUni System Architecture (Module 1)

## 1. Architectural Principles
PocketUni is designed as an institutional university platform providing unified academic information, conversational workflows, and student discovery.

### Non-Negotiable Core Boundaries
1. **Separation of Concerns:** Clean boundary between presentation (React 18), business logic/governance (FastAPI), persistent state (PostgreSQL + SQLAlchemy 2), and document storage (`storage/`).
2. **Authoritative Versioning:** A document or schedule is authoritative only when published by an authorized administrator. Historical versions remain preserved for compliance.
3. **Strict Data Privacy:** Sensitive marks and examination records are partitioned from general public queries and student discovery cards.
4. **No Public Admin Registration:** Administrative permissions are bound to server allowlists and validated identity tokens.

```
+---------------------------------------------------------------------------------+
|                                React 18 Frontend                                |
|  (Landing, College Assistant, Application Agent, Faculty Directory, Profiles,   |
|                 Super Admin Governance Dashboard, Review Modals)                |
+---------------------------------------------------------------------------------+
                                      |  HTTP / REST (JSON)
                                      v
+---------------------------------------------------------------------------------+
|                               FastAPI Backend v1                                |
|   - /auth (Controlled dev auth, JWT, Google OAuth integration point)             |
|   - /documents (Upload validation, extraction pipeline, review & publishing)   |
|   - /academic (Timetables, datesheets, 2026-27 academic calendars)              |
|   - /results (Strict roll-number isolated student results, audited imports)     |
|   - /audit (Tamper-evident audit logs)                                          |
|   - /students & /faculty (Verified profiles, peer discovery)                    |
+---------------------------------------------------------------------------------+
          |                                      |                     |
          v                                      v                     v
+-----------------------+              +-------------------+ +--------------------+
|  SQLAlchemy 2 Models  |              | Extraction Engine | | Local File Storage |
|  (50 Relational DB    |              | - pdfplumber      | | - institutional_   |
|   Tables via Alembic) |              | - python-docx     | |   documents/       |
|                       |              | - openpyxl/pandas | | - resumes/         |
| PostgreSQL / SQLite   |              | - OCR (Tesseract) | | - applications/    |
+-----------------------+              +-------------------+ +--------------------+
```

## 2. Directory Structure

```
PocketUni/
  ├── backend/
  │   ├── app/
  │   │   ├── api/v1/routes/     # FastAPI modular API routers
  │   │   ├── core/              # Config, DB engine, JWT security, permissions
  │   │   ├── models/            # 50 SQLAlchemy 2 relational models
  │   │   ├── schemas/           # Pydantic schemas with strict validation
  │   │   ├── services/          # Extraction, classification, storage, audience
  │   │   └── main.py            # FastAPI main application
  │   ├── alembic/               # Database migration versions
  │   ├── scripts/               # Seed scripts (seed.py, reset_db.py)
  │   ├── tests/                 # Automated pytest suite (12 tests)
  │   └── requirements.txt
  ├── data/
  │   ├── imports/               # CSV templates (students, faculty, results, etc.)
  │   ├── institutional/         # Sample verified test notices and timetables
  │   ├── seed/                  # Raw seed files
  │   └── templates/             # 6 conventional Indian academic application templates
  ├── storage/                   # Local filesystem storage
  │   ├── institutional_documents/
  │   ├── resumes/
  │   ├── application_documents/
  │   └── temporary/
  ├── docs/                      # Complete system documentation
  ├── src/                       # React 18 TypeScript frontend
  ├── .env.example
  └── README.md
```

## 3. Security & Permission Layers
* **JWT Authentication:** Tokens signed with HMAC-SHA256 containing user ID, role, and email.
* **Role Enforcement:** Server-side dependency injection verifies whether the authenticated actor possesses required role (`SUPER_ADMIN`, `FACULTY`, `STUDENT`).
* **Storage Path Validation:** Path traversal attempts (`../`) are detected and rejected. Files are accessed only via authenticated streaming endpoints.
