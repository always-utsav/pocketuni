# PocketUni Repository Audit & Architecture Inventory

This document details the complete structural audit of the PocketUni repository, covering preserved frontend assets, new backend services, database models, and operational integrity.

---

## 1. Preserved Frontend Architecture (React 18 + Vite + TypeScript)

All existing screens, user journeys, React Context, and service engines from the primary product specification have been strictly preserved, styled with refined design tokens, and wired to the backend API:

| Component / File | Purpose & Status | Integration with Real Backend |
|---|---|---|
| `src/components/LandingPage.tsx` | MITS Gwalior hero, animated demo chat, persona login modal | Powered by `/api/v1/auth/dev-login`. Super Admin persona added alongside official faculty and synthetic students. |
| `src/components/ChatView.tsx` | College assistant conversational interface with source citations | Preserved. Ready for Module 2 RAG streaming hook. |
| `src/components/ApplicationAgentChat.tsx` | Finite state machine conversational slot-filling application generator | Connected with templates and `/api/v1/applications`. |
| `src/components/ApplicationListView.tsx` | Student application submission tracking & Faculty application inbox | Real-time status filtering from `/api/v1/applications`. |
| `src/components/ApplicationDetailView.tsx` | Application review, print/download, approval & rejection dialogs | Bound to `/api/v1/applications/{id}/review` with audit logging. |
| `src/components/StudentProfileView.tsx` | Student profile editor, skills tagger, project showcases | Backed by `/api/v1/students/me` with profile completeness metric. |
| `src/components/FacultyProfileView.tsx` | Verified faculty detail view with verified publications and mentor banner | Loaded from `/api/v1/faculty/{id}`. |
| `src/components/FacultyDirectoryView.tsx` | Searchable directory with department filters and mentor badges | Populated live from `/api/v1/faculty`. |
| `src/components/StudentPreviewModal.tsx` | Privacy-aware public student profile preview modal | Connected to `/api/v1/students/public/{id}`. |
| `src/components/NotificationsDropdown.tsx` | In-app notification bell with unread badge | Synced with `/api/v1/communication/notifications`. |
| `src/components/Sidebar.tsx` | Collapsible primary navigation | Added role-gated Super Admin Portal navigation link. |
| `src/components/Navbar.tsx` | Top application header with user badge & current view title | Styled with new Warm Stone & Ink Navy tokens. |
| `src/components/SuperAdminDashboardView.tsx` | **NEW** 15-section administrative portal | Connects to `/api/v1/admin/*`, `/api/v1/documents/*`, `/api/v1/audit`. |
| `src/components/DocumentReviewModal.tsx` | **NEW** Document audit, OCR review & publishing modal | Provides side-by-side extracted text, table inspection, and audience gating. |
| `src/context/AppContext.tsx` | Central state management | Enhanced with token management, API synchronization, and Super Admin state. |
| `src/services/apiClient.ts` | **NEW** Centralized API client | Axios-like fetch wrapper handling JWT bearer auth, error toasts, and multipart uploads. |

---

## 2. Refined Visual Identity Tokens

Replaced raw generic colors with the required institutional design palette:
- **Ink Navy** (`#202C39`): Primary typography, active states, deep structural headers.
- **Slate Blue** (`#536B7A`): Secondary elements, subtle borders, metadata tags.
- **Muted Terracotta** (`#B56F4A`): Accent highlights, active tabs, primary actions.
- **Warm Stone** (`#E8E2D8`): Muted backgrounds, secondary button borders, dividing rules.
- **Paper** (`#F7F6F2`): Application background, card surfaces, canvas.
- **Sage** (`#668477`): Success badges, verified faculty indicators, approval status.

---

## 3. Backend Architecture (FastAPI + SQLAlchemy 2 + PostgreSQL)

```
backend/
├── alembic/                    # Database schema migration tracking
│   ├── versions/
│   │   └── 20261031_0956_1e5131ff1c7b_initial_50_table_schema.py
│   ├── env.py
│   └── alembic.ini
├── app/
│   ├── api/v1/routes/
│   │   ├── academic_records.py # Timetables, calendars, datesheets
│   │   ├── admin.py            # Super Admin operations & configurations
│   │   ├── applications.py     # Student applications & faculty approvals
│   │   ├── audit.py            # Security audit trail queries
│   │   ├── auth.py             # Dev login, token issuance & role verification
│   │   ├── communication.py    # Notifications & messages
│   │   ├── documents.py        # Institutional document uploads & review
│   │   ├── faculty.py          # Faculty directory & verified profiles
│   │   ├── results.py          # Protected marks and grades
│   │   └── students.py         # Student profile management
│   ├── core/
│   │   ├── config.py           # Pydantic v2 settings & database URL resolution
│   │   ├── database.py         # SQLAlchemy engine & session factory
│   │   ├── logging.py          # Structured operational logging
│   │   ├── permissions.py      # Role-based access control dependencies
│   │   └── security.py         # Passlib hashing & JWT token issuance
│   ├── models/                 # 50 registered SQLAlchemy ORM models
│   │   ├── academic.py
│   │   ├── academic_records.py
│   │   ├── admin.py
│   │   ├── application.py
│   │   ├── communication.py
│   │   ├── document.py
│   │   ├── faculty.py
│   │   ├── identity.py
│   │   └── student.py
│   ├── schemas/                # Strict Pydantic v2 validation models
│   ├── services/
│   │   ├── audience_service.py       # Multi-tenant audience filtering
│   │   ├── audit_service.py          # Tamper-evident action logging
│   │   ├── classification_service.py # Metadata heuristic classifier
│   │   ├── extraction_service.py     # Multi-format document parser
│   │   └── storage_service.py        # Path traversal-safe local storage
│   └── main.py                 # FastAPI application factory & CORS setup
├── scripts/
│   ├── reset_db.py             # Clean database teardown utility
│   └── seed.py                 # Seeds official MITS faculty, calendar, and sample data
└── tests/
    └── test_backend.py         # 12 automated end-to-end unit and integration tests
```

---

## 4. Operational Boundaries

- **Module 1 Scope**: Complete local foundation, PostgreSQL database with 50 relational models, development authentication, Super Admin portal, document parsing and audience gating, results privacy, and verified directory.
- **Module 2 Boundary (Preserved & Prepared)**: Vector embeddings (`pgvector`), Gemini API integration, and hybrid RAG search pipeline remain cleanly partitioned behind defined interfaces for subsequent implementation.
