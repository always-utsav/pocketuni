# 🚀 PocketUni — Local Setup & Execution Guide
### Step-by-Step Instructions to Download, Configure, and Run PocketUni Locally

**Repository:** [https://github.com/always-utsav/pocketuni](https://github.com/always-utsav/pocketuni)  
**Institution:** Madhav Institute of Technology & Science (MITS-DU), Gwalior  
**Operating Systems Supported:** Windows 10/11, macOS, Linux (Ubuntu/Debian)

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Method A: Download as ZIP from GitHub](#2-method-a-download-as-zip-from-github)
3. [Method B: Clone via Git (Recommended)](#3-method-b-clone-via-git-recommended)
4. [Database Setup (PostgreSQL)](#4-database-setup-postgresql)
5. [Backend Setup (FastAPI & Python 3.11)](#5-backend-setup-fastapi--python-311)
6. [Frontend Setup (React + Vite + TypeScript)](#6-frontend-setup-react--vite--typescript)
7. [Running the Application](#7-running-the-application)
8. [Testing with the Three-Account Sandbox](#8-testing-with-the-three-account-sandbox)
9. [Troubleshooting & FAQs](#9-troubleshooting--faqs)

---

## 1. Prerequisites

Before starting, ensure you have the following installed on your machine:

| Software | Minimum Version | Check Command | Download Link |
|---|---|---|---|
| **Node.js** | `v20.x` or higher | `node -v` | [nodejs.org](https://nodejs.org/) |
| **npm** | `v10.x` or higher | `npm -v` | Included with Node.js |
| **Python** | `3.11.x` | `python --version` | [python.org](https://www.python.org/downloads/) |
| **PostgreSQL** | `15.x` to `18.x` | `psql -V` | [postgresql.org](https://www.postgresql.org/download/) |
| **Git** *(Optional)* | Any recent | `git --version` | [git-scm.com](https://git-scm.com/) |

> [!NOTE]
> For Windows users, make sure to check **"Add Python to PATH"** during Python installation.

---

## 2. Method A: Download as ZIP from GitHub

If you do not want to use Git command line, download the source code as a ZIP archive:

1. Open your browser and navigate to:  
   👉 **[https://github.com/always-utsav/pocketuni](https://github.com/always-utsav/pocketuni)**
2. Click the green **`<> Code`** button located at the top-right of the file list.
3. In the dropdown, click **`Download ZIP`**.
4. Once downloaded, right-click the `.zip` file (e.g., `pocketuni-main.zip`) and select **Extract All...** (or unzip using 7-Zip / WinRAR).
5. Extract it into an accessible directory (e.g., `C:\PocketUni` or `~/Desktop/Pocket-Uni`).
6. Open your terminal or PowerShell, and navigate to the extracted folder:
   ```bash
   cd path/to/pocketuni-main
   ```

---

## 3. Method B: Clone via Git (Recommended)

If you have Git installed, run:
```bash
git clone https://github.com/always-utsav/pocketuni.git
cd pocketuni
```

---

## 4. Database Setup (PostgreSQL)

PocketUni uses PostgreSQL for institutional memory, user accounts, and real-time events.

### Step 1: Start PostgreSQL Service
Ensure PostgreSQL service is running on your computer.

### Step 2: Create Database
Open `pgAdmin` or your terminal (`psql -U postgres`) and run:
```sql
CREATE DATABASE pocketuni;
```

### Step 3: Configure Backend Environment Variables
Inside the `backend/` folder, create or edit `.env` (or copy from `.env.example`):

```ini
# PostgreSQL Connection
DATABASE_URL=postgresql://postgres:postgrespassword@localhost:5432/pocketuni

# JWT Security
SECRET_KEY=your-secure-secret-key-for-local-development-2026
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Intelligence (Official Google Gemini API)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

# Application URLs
FRONTEND_ORIGIN=http://localhost:5173
```
*(Replace `postgrespassword` with your local PostgreSQL password, and set your free Gemini API key from [aistudio.google.com](https://aistudio.google.com/)).*

---

## 5. Backend Setup (FastAPI & Python 3.11)

Open a terminal window and navigate to the project directory:

### Step 1: Create a Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv backend\.venv
  .\backend\.venv\Scripts\Activate.ps1
  ```
  *(If execution policies block script activation, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **On macOS / Linux:**
  ```bash
  python3 -m venv backend/.venv
  source backend/.venv/bin/activate
  ```

### Step 2: Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install "psycopg[binary]" pytest httpx python-multipart python-jose[cryptography] passlib[bcrypt]
```

### Step 3: Seed Database with MITS Institutional Data
Run the institutional database seed script to populate official faculty profiles, departments, course structures, and timetables:
```bash
python -m backend.scripts.seed
```
*(You will see confirmation logs initializing departments, students, faculty, and knowledge chunks).*

---

## 6. Frontend Setup (React + Vite + TypeScript)

Open a **second terminal window** (keep the backend terminal open) and navigate to the project root:

```bash
cd path/to/pocketuni
```

### Step 1: Install Dependencies
```bash
npm install
```

### Step 2: Verify Frontend Configuration
The frontend automatically points to `http://localhost:8000/api/v1`. If you need custom URLs, you can create a `.env` in the root:
```ini
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 7. Running the Application

To run the complete system, you will start the Backend and Frontend concurrently in two terminals:

### Terminal 1 — Start FastAPI Backend:
```bash
# Windows
.\backend\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# macOS / Linux
source backend/.venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Docs & Swagger UI will be available at: **`http://localhost:8000/docs`**

### Terminal 2 — Start React Vite Frontend:
```bash
npm run dev
```
- Frontend application will be live at: **`http://localhost:5173`**

---

## 8. Testing with the Three-Account Sandbox

PocketUni features a built-in **Three-Account Sandbox** that allows testing all user roles simultaneously without manual registration:

Open your browser at **`http://localhost:5173`** and click **"Try Test Sandbox"** on the landing page:

| Persona | Role | What You Can Test |
|---|---|---|
| **🎓 Student Sandbox** | B.Tech Student (`Aarav Sharma`) | Ask questions about timetables, fees, syllabi; draft formal letters; submit applications to mentors; discover peers. |
| **👨‍🏫 Faculty Sandbox** | Academic Mentor (`Dr. Mausam Chouksey`) | Check faculty inbox; review submitted applications; approve, reject, or request revisions; update consultation hours. |
| **🛡️ Super Admin Sandbox** | Platform Administrator (`mahi gupta`) | Inspect database statistics, view audit logs, edit student/faculty records in real-time, test crawler & roster sync. |

> [!TIP]
> **Multi-Tab Live Test:** Open one tab in Student Sandbox and another in Faculty Sandbox (using an Incognito window). Submit a leave request from the student tab — notice it instantly appears in the faculty inbox via WebSockets without refreshing the page!

---

## 9. Troubleshooting & FAQs

### Q1: `ModuleNotFoundError: No module named 'psycopg'` or similar
Ensure you activated the virtual environment in your terminal before running commands (`.\backend\.venv\Scripts\Activate.ps1`).

### Q2: Port 8000 or 5173 is already in use
- To use another backend port: `uvicorn backend.app.main:app --reload --port 8001`
- To use another frontend port: `npm run dev -- --port 3000`

### Q3: How to run automated tests locally?
Run the full 83-test pytest suite:
```bash
python -m pytest backend/tests/ -v
```

---
*Developed for Madhav Institute of Technology & Science (MITS-DU), Gwalior.*
