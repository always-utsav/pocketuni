# PocketUni API Reference (Module 1 & Module 2: Foundation, AI Intelligence & Workflows)

**Base URL**: `http://localhost:8000/api/v1`  
**Interactive Swagger UI**: `http://localhost:8000/docs`  
**ReDoc**: `http://localhost:8000/redoc`  
**Health Check**: `GET /api/v1/health`

---

## 1. Authentication & Identity (`/auth`)

### `POST /auth/dev-login`
Authenticate in local development mode without external OAuth providers.
- **Request Body**:
  ```json
  {
    "email": "utsavkumawat05@gmail.com",
    "role": "SUPER_ADMIN",
    "full_name": "Utsav Kumawat"
  }
  ```
- **Security Check**:
  - `SUPER_ADMIN` role is strictly verified against the server-side allowlist (`SUPER_ADMIN_ALLOWLIST`). Frontend cannot spoof admin access.
  - `@mitsgwl.ac.in` and `@example.invalid` domains map to `STUDENT`.
  - `@mitsgwalior.in` maps to `FACULTY`.
- **Response `200 OK`**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "e44d3204-7a13-4482-b7d6-3e790757aeb8",
      "email": "utsavkumawat05@gmail.com",
      "full_name": "Utsav Kumawat",
      "roles": ["SUPER_ADMIN"],
      "primary_role": "SUPER_ADMIN",
      "is_demo": false
    }
  }
  ```

### `GET /auth/me`
Retrieve currently authenticated user identity and effective roles.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**: User profile with roles and institutional metadata.

---

## 2. Students & Profile Management (`/students`)

### `GET /students/me`
Get current student's full profile including bio, skills, projects, and visibility settings.
- **Permissions**: `STUDENT` role only.

### `PUT /students/me`
Update current student's editable profile information.
- **Request Body**:
  ```json
  {
    "bio": "AI Researcher passionate about Transformers and Edge Computing",
    "github_url": "https://github.com/student",
    "linkedin_url": "https://linkedin.com/in/student",
    "skills": ["Python", "FastAPI", "PyTorch", "TypeScript"],
    "projects": [
      {
        "title": "PocketUni Core",
        "description": "Full-stack institutional platform",
        "technologies": ["React", "FastAPI", "PostgreSQL"],
        "project_url": "https://github.com/pocketuni"
      }
    ]
  }
  ```

### `GET /students/public/{student_id}`
Retrieve public student profile for discovery.
- **Permissions**: Any authenticated user.
- **Privacy**: Respects `ProfileVisibility` flags. Hidden fields (contact, private projects) are redacted server-side.

---

## 3. Faculty Directory (`/faculty`)

### `GET /faculty`
Search and filter verified faculty directory.
- **Query Params**:
  - `search` (string, optional): Search by name, designation, or specialization.
  - `department` (string, optional): Filter by department name.
- **Response `200 OK`**:
  ```json
  [
    {
      "id": "c88f1bb8-faec-44f2-9599-4dcfc9687e35",
      "name": "Dr. Mausam Chouksey",
      "designation": "Assistant Professor",
      "department": "Centre for Artificial Intelligence",
      "cabin_location": "CAI Block, Room 204",
      "email": "mchouksey@mitsgwalior.in",
      "research_interests": ["Deep Learning", "Generative AI", "NLP", "Machine Vision"],
      "verification_status": "VERIFIED_OFFICIAL_SOURCE",
      "is_mentor": true,
      "mentor_association_details": "MITS Centre for AI Lead Project Guide"
    }
  ]
  ```

### `GET /faculty/{faculty_id}`
Get detailed faculty profile including education, experience, and peer-reviewed publications.

---

## 4. Student Applications & Approvals (`/applications`)

### `GET /applications`
List applications. Students see their submitted applications; faculty see applications shared with them.
- **Query Params**: `status` (`DRAFT`, `PENDING_REVIEW`, `APPROVED`, `REJECTED`).

### `POST /applications`
Create and submit a formal student application.
- **Request Body**:
  ```json
  {
    "application_type": "NO_OBJECTION_CERTIFICATE",
    "subject": "Request for NOC for Summer AI Research Internship",
    "faculty_id": "c88f1bb8-faec-44f2-9599-4dcfc9687e35",
    "content": "Respected Sir, I request permission to undergo an off-campus internship...",
    "metadata": {
      "company_name": "Indian Institute of Science",
      "duration": "8 weeks"
    }
  }
  ```

### `GET /applications/{app_id}`
Get application detail with immutable status change history and reviewer feedback.

### `POST /applications/{app_id}/review`
Review, approve, or reject an application.
- **Permissions**: Assigned faculty or `SUPER_ADMIN`.
- **Request Body**:
  ```json
  {
    "action": "APPROVE",
    "remarks": "Approved. Maintain required attendance standards during term."
  }
  ```

---

## 5. Institutional Documents (`/documents`)

### `POST /documents/upload`
Upload an official institutional document (PDF, DOCX, XLSX, CSV, TXT, scanned images).
- **Permissions**: `SUPER_ADMIN` only.
- **Multipart Form Data**:
  - `file`: Document file binary
  - `title`: "Academic Calendar 2026-27"
  - `category`: "ACADEMIC_CALENDAR"
  - `department_id` (optional): Department UUID
  - `programmes` (optional): `["B.Tech", "M.Tech"]`
  - `target_roles` (optional): `["STUDENT", "FACULTY"]`
- **Response**: Triggers automated extraction job and returns `document_id`, `version_id`, `job_id`.

### `GET /documents`
List published documents filtered by user's audience scope.
- Students receive only documents matching their department, programme, and year.
- Faculty receive faculty notices and institutional guidelines.
- Super Admins receive all documents.

### `GET /documents/{document_id}/review`
Get full extracted text, detected structured tables, and heuristic metadata for administrative audit.
- **Permissions**: `SUPER_ADMIN` only.

### `POST /documents/{document_id}/publish`
Publish a reviewed document or archive an existing publication.
- **Permissions**: `SUPER_ADMIN` only.
- **Request Body**:
  ```json
  {
    "action": "PUBLISH",
    "remarks": "Verified by Office of the Registrar"
  }
  ```

---

## 6. Academic Records & Results (`/academic-records` & `/results`)

### `GET /academic-records/timetable`
Get official timetable entries scoped to the authenticated student's semester and branch.

### `GET /academic-records/datesheet`
Get examination datesheet entries for active examination sessions.

### `GET /academic-records/calendar`
Get institutional academic calendar entries for the 2026-2027 academic session.

### `GET /results/my-results`
Strictly retrieve only the authenticated student's own verified examination results.
- **Permissions**: `STUDENT` role. Cross-student access is strictly forbidden with HTTP 403.
- **Response**: SGPA, CGPA, semester, session, and individual subject credits and grades.

---

## 7. Super Admin Management (`/admin` & `/audit`)

### `GET /admin/stats`
Institution-wide telemetry: user count, document volume, pending extraction jobs, active notices.

### `GET /admin/users`
List and manage registered platform accounts.

### `POST /admin/super-admins`
Designate a new verified Super Admin account (secondary admin onboarding).

### `GET /audit`
Query system audit trail with timestamp, user ID, client IP, action type, and JSON payload diffs.
- **Permissions**: `SUPER_ADMIN` only.


---

## 8. Chat & Grounded Institutional RAG (`/chat`)

### `GET /chat/conversations`
List all conversation sessions for the authenticated user.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Array of conversation objects (id, title, created_at, updated_at).

### `POST /chat/conversations`
Create a new conversation session.
- **Request Body**:
  ```json
  {
    "title": "Semester IV Scheme Inquiries"
  }
  ```

### `GET /chat/conversations/{conversation_id}/messages`
Retrieve full message history for a conversation.
- **Response**: Array of messages with sender, role, content, and citations.

### `POST /chat/conversations/{conversation_id}/messages`
Send a user prompt, perform hybrid dense/lexical RAG search over institutional document chunks, and synthesize grounded response via Google Gemini (`gemini-2.5-flash`).
- **Request Body**:
  ```json
  {
    "content": "What are the subjects and credit distribution in 2nd year AI scheme?"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "id": "msg-uuid",
    "conversation_id": "conv-uuid",
    "role": "ASSISTANT",
    "content": "In the 2nd year B.Tech Artificial Intelligence scheme (session 2025-26)...",
    "citations": [
      {
        "document_id": "doc-uuid",
        "title": "II Year Scheme admitted in session 2025-26.pdf",
        "page_number": 1,
        "score": 0.88
      }
    ],
    "grounded": true
  }
  ```

### `POST /chat/stream`
Server-Sent Events (SSE) streaming endpoint for real-time token delivery with grounding metadata.

---

## 9. Conversational Application Agent & Word Export (`/applications`)

### `POST /applications/agent-chat`
Multi-turn conversational slot-filling agent assisting students in drafting formal applications.
- **Request Body**:
  ```json
  {
    "message": "I need to apply for 3 days sick leave starting tomorrow",
    "current_slots": {
      "application_type": "LEAVE_OF_ABSENCE"
    }
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "reply": "I've noted your leave request. Please confirm your expected start and end dates...",
    "slots": {
      "application_type": "LEAVE_OF_ABSENCE",
      "student_name": "Utsav Kumawat",
      "roll_number": "0901AI231001",
      "reason": "Sick leave"
    },
    "is_complete": false,
    "missing_slots": ["start_date", "end_date"]
  }
  ```

### `GET /applications/{id}/docx`
Download formally compiled application as an official Word document (`.docx`) with MITS letterhead and signature block.
- **Permissions**: Submitting student, assigned faculty reviewer, or Super Admin.

---

## 10. Student Discovery & Collaboration (`/students`)

### `GET /students/discover`
Search and filter student collaborator directory with explainable match reasons.
- **Query Params**:
  - `skills` (optional): Filter by comma-separated skills (e.g. `Python,PyTorch`).
  - `branch` (optional): Filter by department / branch.
  - `interests` (optional): Filter by research interest keywords.
  - `year` (optional): Filter by year of study.
- **Privacy & Security**: Requesting user is excluded; private profiles are omitted; confidential contact details and marks are redacted.

### `GET /students/{id}/preview`
Retrieve public profile modal data (verified achievements, projects, skills).

---

## 11. Google OAuth 2.0 (`/auth`)

### `GET /auth/oauth-status`
Check whether Google OAuth 2.0 client credentials are configured.
- **Response**: `{"google_oauth_configured": false, "active_mode": "LOCAL_DEV_AUTH"}`

### `GET /auth/google/url`
Generate Google OAuth 2.0 authorization URL with CSRF state protection.

### `POST /auth/google/callback`
Validate authorization code / token from Google, verify email allowlist / domain, and return JWT.

### `POST /auth/context-switch`
Allows an authenticated Super Admin to switch their active dashboard context between `SUPER_ADMIN`, `STUDENT`, and `FACULTY` views with full audit logging and zero data fabrication.
- **Permissions**: `SUPER_ADMIN` only.
- **Request Body**: `{"target_context": "STUDENT"}`
- **Response**: `{"access_token": "...", "active_context": "STUDENT", "role": "SUPER_ADMIN"}`

---

## 12. Super Admin AI Diagnostics & Indexing (`/admin`)

### `GET /admin/ai-status`
Check health and connectivity of Google Gemini chat model (`gemini-2.5-flash`), embedding model (`gemini-embedding-001`), and total indexed vector chunks in PostgreSQL.

### `POST /admin/documents/{id}/index`
Trigger structure-aware chunking and vector embedding generation for a published document.

### `POST /admin/diagnostics/rag-test`
Perform diagnostic hybrid vector + keyword search test on an arbitrary query and inspect raw chunk scores and top matching passages.
- **Permissions**: `SUPER_ADMIN` only.

---

## 13. Institutional Roster & Excel Synchronization (`/admin/roster`)

### `POST /admin/roster/preview`
Pre-validates an uploaded `.xlsx` student or faculty workbook without committing changes. Returns valid rows, error rows, duplicate count, and preview objects.
- **Form Data**: `file` (UploadFile), `entity_type` (`STUDENT` or `FACULTY`)
- **Permissions**: `SUPER_ADMIN` only.

### `POST /admin/roster/import`
Transactionally commits a validated `.xlsx` workbook into PostgreSQL 18 and triggers an atomic export update to the local disk mirror.
- **Form Data**: `file` (UploadFile), `entity_type` (`STUDENT` or `FACULTY`)
- **Permissions**: `SUPER_ADMIN` only.

### `GET /admin/roster/export/{entity_type}`
Generates and downloads the current PostgreSQL roster as an official Excel workbook (`pocketuni_students.xlsx` or `pocketuni_faculty.xlsx`).
- **Path Param**: `entity_type` (`STUDENT` or `FACULTY`)
- **Permissions**: `SUPER_ADMIN` only.

### `GET /admin/roster/sync-status`
Returns recent roster import batch telemetry and pending background Excel sync jobs.
- **Permissions**: `SUPER_ADMIN` only.

### `PUT /admin/roster/users/{id}/institutional-fields`
Updates locked institutional metadata (e.g., section, semester, designation) for a student or faculty record.
- **Permissions**: `SUPER_ADMIN` only.

### `POST /admin/roster/users/{id}/status`
Toggles account activation status (`is_active: true / false`).
- **Permissions**: `SUPER_ADMIN` only.

---

## 14. Faculty Profile Self-Management (`/faculty`)

### `GET /faculty/me`
Retrieves authenticated faculty member's full profile including locked institutional fields (`designation`, `department`, `qualifications`, `officialProfileUrl`) and editable fields.
- **Permissions**: `FACULTY` or `SUPER_ADMIN` in faculty context.

### `PUT /faculty/me`
Updates user-editable faculty attributes (`bio`, `officeLocation`, `officeHours`, `emailPublic`, `phonePublic`, `researchAreas`, `areasOfExpertise`). Fixed institutional fields cannot be modified.
- **Permissions**: `FACULTY` or `SUPER_ADMIN`.

---

## 15. MITS Web Ecosystem Ingestion & Portals Directory (`/website`)

### `GET /website/sources`
Lists registered official MITS web crawl targets with crawl frequency, depth, total discovered pages, and last success timestamps.
- **Permissions**: `SUPER_ADMIN` only.

### `POST /website/sources`
Registers a new institutional web crawl source with category and depth parameters.
- **Permissions**: `SUPER_ADMIN` only.

### `POST /website/crawl`
Executes the polite web crawler across registered MITS domains, extracts clean semantic text, hashes content for deduplication, and generates vector embeddings.
- **Permissions**: `SUPER_ADMIN` only.
- **Request Body**: `{"max_pages": 10, "source_id": null}`

### `GET /website/portals`
Returns the public institutional directory of MITS e-governance systems (AMS, MIS, IMS, Moodle, Alumni, NEC, OSM, RRS) with access URLs, authentication requirements, and service descriptions.
- **Permissions**: Authenticated users (`STUDENT`, `FACULTY`, `SUPER_ADMIN`).

### `GET /website/stats`
Telemetry summary returning total registered sources, crawled pages, extracted documents, and indexed RAG web chunks.
- **Permissions**: `SUPER_ADMIN` only.
