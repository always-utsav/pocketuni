# PocketUni — Conversational Academic AI Assistant & Knowledge Platform
**Institution:** Madhav Institute of Technology & Science (MITS-DU), Gwalior  
**Departments Supported:** Centre for Artificial Intelligence (CAI), Computer Science & Engineering (CSE), Internet of Things (IoT)  
**Technology Stack:** React 18, TypeScript, Vite, Tailwind CSS, Python 3.11, FastAPI, PostgreSQL 18.6, SQLAlchemy 2, Alembic, Google Gemini SDK  

---

## 🏛 Visual Identity & Institutional Design System

PocketUni uses an authoritative institutional palette tailored for academic dignity and modern SaaS productivity:

| Token | Name | Hex Code | Visual Application |
|---|---|---|---|
| `midnight` | Deep Midnight | `#14252B` | Primary headings, dark accents, brand badge |
| `forest` | Forest Teal | `#176B68` | Secondary navigation, verified pills, icons |
| `porcelain` | Porcelain | `#F5F3EE` | Clean content surfaces, canvas, cards |
| `sand` | Warm Sand | `#E7DFD2` | Borders, subtle card dividers, neutral chips |
| `copper` | Burnt Copper | `#B96D47` | High-emphasis CTAs, interactive highlights |
| `sage` | Soft Sage | `#8A9B87` | Success badges, verified student indicators |
| `charcoal` | Charcoal | `#273238` | Body typography, secondary metadata |

---

## 🚀 Key Capabilities & Product Features

### 1. Three-Account Institutional Sandbox
Instant one-click sandbox environments for comprehensive pair testing without email exposure or credential friction:
- **Student Sandbox:** B.Tech CAI / AIR student persona with full peer discovery, timetable lookup, syllabus queries, and formal application drafting.
- **Faculty Sandbox:** Designated CAI Mentor (Dr. Mausam Chouksey) persona receiving formal student applications, approving/rejecting drafts, and requesting revisions in real-time.
- **Super Administrator Sandbox:** Platform Architect & Administrator (`utsavkumawat05@gmail.com`) persona with live system metrics, knowledge ingestion, crawler triggers, and roster oversight.

### 2. Conversational Institutional RAG & Progressive Streaming
- **Server-Sent Events (SSE):** Progressive token streaming from Google Gemini (`gemini-2.5-flash`) via `/api/v1/chat/conversations/{id}/stream`.
- **Grounded Source Citations:** AI answers cite official MITS documents with page numbers, document category, and relevance snippets.
- **Rate-Limit Resilience:** Safe backoff and grounded institutional fallback if upstream free-tier API quotas are temporarily exhausted.
- **Strict Isolation:** User conversations are isolated at the database level (`user_id == current_user.id`) and scoped on the frontend (`pocketuni_chats_${currentUser.id}`).

### 3. Authoritative Timetable & Availability Intelligence
- **Scanned Document Hours:** Exact period slots calibrated to official MITS timetables (July–Dec 2026):
  - Period 1: 10:00 AM – 11:00 AM
  - Period 2: 11:00 AM – 12:00 PM
  - Period 3: 12:00 PM – 01:00 PM
  - Lunch Break: 01:00 PM – 02:00 PM
  - Period 4: 02:00 PM – 03:00 PM
  - Period 5: 03:00 PM – 04:00 PM
  - Period 6: 04:00 PM – 05:00 PM
- **Zero Unsafe Defaults:** Queries without branch/semester context prompt for honest clarification rather than making silent assumptions.
- **Known-Coverage Complement:** Faculty without published timetable schedules are marked as `unknown_coverage_faculty` rather than erroneously reported as free.

### 4. Real-Time WebSocket Synchronization
- Authenticated bidirectional WebSocket channel at `/api/v1/ws?token=...`
- Dispatches live updates for application status transitions (`application_status_changed`), faculty profile updates, and institutional announcements.

### 5. Multi-Department Faculty Directory & Enriched Profiles
- Verified profiles for Dr. Shradha Dubey (CSE, Medical Image Processing & Pose Estimation), Dr. Aftab Ahmed Ansari (IoT, Wireless Sensor Networks), Prof. Ramnaresh Sharma (CSE), and all CAI, CSE, and IoT faculty members.
- Dynamic department filtering (`All`, `CAI`, `CSE`, `IoT`).
- Masked internal phone numbers protecting faculty privacy unless viewed by the profile owner or Super Admin.

### 6. Formal Application Workflow & Outbox Security
- AI-guided conversational letter drafting for Leaves, NOCs, Bonafide Certificates, and Venue Permissions.
- State machine: `draft` ➔ `sent` ➔ `approved` / `rejected` / `revision_requested`.
- Outbox inspection (`/api/v1/applications/outbox/queue`) restricted strictly to Super Administrators (403 for students and faculty).

---

## 🛠 Local Setup & Running Instructions (Windows 11)

### Prerequisites
- **Node.js** (v18+) and **npm**
- **Python** (3.11+)
- **PostgreSQL 18** (running locally on port 5432)

---

### Step 1: Environment Configuration
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Ensure your `.env` contains:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pocketuni
DB_USER=postgres
DB_PASSWORD=your_actual_postgres_password
SUPER_ADMIN_ALLOWLIST=["utsavkumawat05@gmail.com"]
GEMINI_API_KEY=your_gemini_api_key
```

---

### Step 2: Database Initialization & Migrations
```powershell
# Activate backend virtual environment
.\backend\.venv\Scripts\Activate.ps1

# Run database migrations to latest revision (d4a9ef182390)
alembic -c backend/alembic.ini upgrade head

# Run seed script to populate verified MITS institutional data
python backend/scripts/seed.py
```

---

### Step 3: Run the Backend Server
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The FastAPI backend runs at `http://localhost:8000`. Swagger documentation is available at `http://localhost:8000/docs`.

---

### Step 4: Run the Frontend Application
In a separate terminal:
```powershell
npm install
npm run dev
```
The Vite development server runs at `http://localhost:5173` (or `http://localhost:3000`).

---

### Step 5: Run Automated Tests
```powershell
# Backend pytest test suite
$env:PYTHONPATH="."; .\backend\.venv\Scripts\pytest backend\tests\test_master_transformation.py -v

# Frontend production build check
npm run build
```

---

## 📂 Project Architecture

```
Pocket-Uni/
├── backend/                       # Python 3.11 FastAPI backend
│   ├── alembic/                   # Database schema migrations (Alembic)
│   ├── app/
│   │   ├── api/v1/routes/         # REST & WebSocket route controllers
│   │   ├── core/                  # Security, database configuration, permissions
│   │   ├── models/                # SQLAlchemy database models
│   │   ├── schemas/               # Pydantic v2 schemas
│   │   └── services/              # RAG engine, intent router, timetable, realtime WS
│   ├── scripts/                   # Seed & enrichment scripts
│   └── tests/                     # Automated test suites
├── src/                           # React 18 TypeScript Vite frontend
│   ├── components/                # Application views, modals, cards, navigation
│   ├── context/                   # AppContext (user-scoped state, WebSocket listener)
│   ├── services/                  # apiClient (REST, SSE streaming), realtimeClient (WS)
│   └── types/                     # TypeScript shared interfaces
├── data/                          # Authoritative institutional source files
├── storage/                       # Local filesystem storage (resumes, avatars, documents)
└── docs/                          # Architectural documentation & audit reports
```

---

## 🔒 Confidentiality & Security Notice
In compliance with MITS academic guidelines:
- Confidential student marks lists and internal assessments are permanently excluded from AI retrieval indexes (`RESTRICTED_CONFIDENTIAL`).
- Outbox inspection is strictly role-gated to Super Administrators.
- Voluntary avatar uploads undergo extension validation, 2MB size enforcement, and PIL image re-encoding.
