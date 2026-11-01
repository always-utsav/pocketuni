# Module 2 Manual Setup & Run Guide

## 1. Prerequisites
- **Operating System**: Windows 10/11
- **Python**: Python 3.11+
- **Node.js**: Node 18+ & npm
- **Database**: PostgreSQL 18 running locally on `localhost:5432` with database `pocketuni`
- **Tesseract OCR**: Installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **Google Gemini API Key**: Acquired from Google AI Studio

---

## 2. Environment Verification

Ensure `.env` in the root and `backend/.env` contain:
```env
# PostgreSQL 18
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pocketuni
DB_USER=postgres
DB_PASSWORD="your-postgres-password"

# Google Gemini API
GEMINI_API_KEY="your-gemini-api-key"
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

# App Secrets
SECRET_KEY="your-jwt-secret-key"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 3. Database Migrations & Ingestion

Run the following commands in PowerShell from the repository root:

```powershell
# 1. Activate backend environment
.\backend\.venv\Scripts\Activate.ps1

# 2. Run Alembic migrations to current head (52 tables)
alembic -c backend/alembic.ini upgrade head

# 3. Ingest official MITS CAI documents and index vector chunks
python -m backend.app.ingest_real_docs
```

---

## 4. Running the Test Suite

Execute all tests (Module 1 foundation + Module 2 AI/RAG/Workflows):

```powershell
.\backend\.venv\Scripts\python.exe -m pytest .\backend\tests\test_backend.py .\backend\tests\test_module2.py -v
```
*Expected Result: All 29 tests passing.*

---

## 5. Starting the Application

### A. Start the FastAPI Backend
```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`
- AI Health: `http://localhost:8000/api/v1/admin/ai-status`

### B. Start the React Frontend
In a separate terminal:
```powershell
npm run dev
```
- Web Application: `http://localhost:5173`
