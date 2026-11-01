# PocketUni Backend Service (Module 1)

FastAPI + SQLAlchemy 2 + PostgreSQL backend for PocketUni at MITS Gwalior.

---

## 🚀 Quick Start (Windows PowerShell)

### 1. Environment Setup

```powershell
# Navigate to backend directory
cd C:\Users\utsav\Desktop\Pocket-Uni\backend

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# (Optional) Verify dependencies
python -m pip list
```

### 2. Configure Environment Variables

Create `.env` at the project root (`Pocket-Uni/.env`) based on `.env.example`:

```env
ENVIRONMENT=development
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pocketuni
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_postgres_password_here
SECRET_KEY=pocketuni-insecure-dev-secret-key-change-in-prod-2026
SUPER_ADMIN_ALLOWLIST=["utsavkumawat05@gmail.com"]
```

> **Note**: If `POSTGRES_PASSWORD` is left empty, the application automatically defaults to a local SQLite database (`pocketuni_dev.db`) for zero-friction local testing.

### 3. Database Initialization & Seeding

```powershell
# Run database seed script (creates admin, official faculty, demo students, and 2026-27 calendar)
python .\scripts\seed.py
```

### 4. Run the Backend API Server

```powershell
# Start Uvicorn development server on port 8000
python -m uvicorn backend.app.main:app --reload --port 8000 --host 127.0.0.1
```

- **API Root**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`
- **Health Check**: `http://127.0.0.1:8000/api/health`

### 5. Run Automated Backend Tests

```powershell
python -m pytest tests\test_backend.py -v
```

---

## 🏛 Database Schema & Alembic Migrations

To apply or generate new Alembic migrations:

```powershell
# Check current migration revision
python -m alembic -c alembic.ini current

# Upgrade database to head revision
python -m alembic -c alembic.ini upgrade head
```

---

## 🔒 Security & Roles

- **SUPER_ADMIN**: Strictly server-side allowlisted (`utsavkumawat05@gmail.com`).
- **FACULTY**: Scoped to institutional `@mitsgwalior.in` domain.
- **STUDENT**: Scoped to institutional `@mitsgwl.ac.in` and `@example.invalid` domains.
