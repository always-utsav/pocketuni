# PocketUni — AI-Powered University Technology Platform for MITS Gwalior

An enterprise full-stack platform built for **Madhav Institute of Technology & Science (MITS), Gwalior**, featuring an interactive React 18 frontend and a modular Python / FastAPI / PostgreSQL backend.

---

## 🎨 Refined Visual Identity & Design System

PocketUni implements an institutional design system balancing academic authority with a modern SaaS feel:

- **Ink Navy** (`#202C39`): Primary typography, active states, deep structural headers.
- **Slate Blue** (`#536B7A`): Secondary elements, subtle borders, metadata tags.
- **Muted Terracotta** (`#B56F4A`): Accent highlights, active tabs, primary actions.
- **Warm Stone** (`#E8E2D8`): Muted backgrounds, secondary button borders, dividing rules.
- **Paper** (`#F7F6F2`): Application background, card surfaces, canvas.
- **Sage** (`#668477`): Success badges, verified faculty indicators, approval status.

---

## 🏛 Architecture Overview

```
Pocket-Uni/
├── backend/                       # Python 3.11 + FastAPI + SQLAlchemy 2 + Alembic
│   ├── alembic/                   # Database schema migrations (50 relational tables)
│   ├── app/
│   │   ├── api/v1/routes/         # 10 REST controllers (auth, students, faculty, etc.)
│   │   ├── core/                  # Security, database sessions, permissions
│   │   ├── models/                # SQLAlchemy ORM models
│   │   ├── schemas/               # Pydantic v2 validation models
│   │   └── services/              # Storage, multi-format extraction, audience filtering
│   ├── scripts/                   # Database seed and reset utilities
│   └── tests/                     # Automated unit and integration test suite
├── src/                           # React 18 + TypeScript + Vite + Tailwind CSS
│   ├── components/                # All existing screens + Super Admin Dashboard
│   ├── context/                   # AppContext with real API synchronization
│   └── services/apiClient.ts      # Centralized HTTP client with JWT auth
├── data/
│   ├── imports/                   # CSV templates for students, faculty, and results
│   ├── institutional/             # Sample PDF, DOCX, and XLSX records
│   └── templates/                 # 6 formal academic application templates
├── storage/                       # Local file storage (documents, resumes, uploads)
└── docs/                          # Comprehensive architecture and API documentation
```

---

## 🚀 Running PocketUni Locally (Windows PowerShell)

### Prerequisites
- **Node.js** (v18+) and **npm**
- **Python** (3.11+)
- **PostgreSQL** (installed locally on `localhost:5432`)

---

### Step 1: Configure Environment

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set your local PostgreSQL password:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pocketuni
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_postgres_password_here
SUPER_ADMIN_ALLOWLIST=["utsavkumawat05@gmail.com"]
```

*(If `POSTGRES_PASSWORD` is omitted, the backend automatically defaults to a local SQLite database for zero-configuration testing).*

---

### Step 2: Initialize & Seed the Database

```powershell
# Activate backend virtual environment
.\backend\.venv\Scripts\Activate.ps1

# Run the seeding script
python .\backend\scripts\seed.py
```

This provisions:
- Initial Super Admin account: `utsavkumawat05@gmail.com`
- 22 official MITS CAI faculty records (including **Dr. Mausam Chouksey**, designated CAI faculty guide)
- 4 synthetic demo students (`@example.invalid`)
- Academic calendar for 2026–27
- Sample timetables, examination datesheets, and confidential marks

---

### Step 3: Start the Backend API Server

In a PowerShell terminal:

```powershell
.\backend\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload --port 8000 --host 127.0.0.1
```

- Backend runs at: `http://127.0.0.1:8000`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`

---

### Step 4: Start the Frontend Application

In a separate PowerShell terminal:

```powershell
npm run dev
```

- Frontend runs at: `http://localhost:5173`

---

### Step 5: Run Automated Tests & Builds

```powershell
# Run backend test suite (12 tests)
.\backend\.venv\Scripts\Activate.ps1
python -m pytest backend\tests\test_backend.py -v

# Run frontend production build
npm run build
```

---

## 👤 User Personas & Testing Accounts

| Persona / Role | Email | Access Scope |
|---|---|---|
| **Super Admin** | `utsavkumawat05@gmail.com` | Complete access to the 15-section Super Admin governance portal. |
| **Faculty (Mentor)** | `mchouksey@mitsgwalior.in` | **Dr. Mausam Chouksey** (CAI Assistant Professor & Lead Guide). Can review and approve/reject applications. |
| **Faculty (HOD)** | `manish.dixit@mitsgwalior.in` | Verified faculty directory and application review. |
| **Student (AI Cohort)** | `meera.patel@example.invalid` | 4th-Year AI Research student. Application agent, own profile, and results. |
| **Student (CSE Cohort)** | `aarav.sharma@example.invalid` | 2nd-Year CSE student. Class timetables and academic calendar. |

---

## 📚 Documentation Index

- [API Reference](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/API_REFERENCE.md)
- [Repository & Architecture Audit](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/REPOSITORY_AUDIT.md)
- [Database Schema Specification](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/DATABASE_SCHEMA.md)
- [Document Extraction Pipeline](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/DOCUMENT_EXTRACTION.md)
- [Super Admin Operational Guide](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/SUPER_ADMIN_GUIDE.md)
- [Data Import & Ingestion Guide](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/DATA_IMPORT_GUIDE.md)
- [Manual Setup Checklist](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/MANUAL_SETUP_CHECKLIST.md)
- [Module 1 Completion Report](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/MODULE_1_COMPLETION_REPORT.md)
- [Module 2 Handoff & Prerequisites](file:///C:/Users/utsav/Desktop/Pocket-Uni/docs/MODULE_2_HANDOFF.md)
