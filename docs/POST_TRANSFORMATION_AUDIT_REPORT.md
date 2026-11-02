# POCKETUNI — POST-TRANSFORMATION CRITICAL TECHNICAL AUDIT REPORT
**Product:** PocketUni — Conversational Academic AI Platform  
**Institution:** Madhav Institute of Technology & Science (MITS-DU), Gwalior  
**Departments Covered:** Centre for Artificial Intelligence (CAI), Computer Science & Engineering (CSE), Internet of Things (IoT)  
**Date of Audit & Remediation:** November 2, 2026  
**Operating Environment:** Windows 11, PostgreSQL 18.6, Python 3.11 FastAPI, React 18 TypeScript Vite  

---

## EXECUTIVE SUMMARY

A critical post-transformation technical and security audit was conducted on the PocketUni codebase, database schemas, and AI retrieval infrastructure. All eleven identified audit discrepancies (11.1 through 11.11), along with real-time WebSocket synchronization, progressive Gemini streaming, faculty profile enrichment, and three-account sandbox experiences, have been resolved, verified with automated tests, and confirmed against authoritative institutional documents and official MITS-DU portal records.

---

## 1. AUDIT FINDINGS, ROOT CAUSES, AND REMEDIATIONS

### 11.1 Google OAuth 405 Method Not Allowed & Local Authentication
- **Defect:** Navigating to or redirected from Google OAuth consent screen to `/api/v1/auth/google/callback` triggered `405 Method Not Allowed`.
- **Root Cause:** The backend callback endpoint was registered solely as `@router.post("/google/callback")`. Browser consent redirects follow OAuth 2.0 Authorization Code Flow specifications via HTTP `GET` requests with `?code=...&state=...`.
- **Remediation:** 
  - Added `@router.get("/google/callback")` in `backend/app/api/v1/routes/auth.py`.
  - Parses code and state parameters and seamlessly completes token exchange, redirecting cleanly to the frontend origin.
  - Implemented `@router.post("/sandbox-login")` and `@router.get("/sandbox-login")` for deterministic, zero-friction sandbox logins.

### 11.2 Three-Account Sandbox Experience & Chat Isolation
- **Defect:** Unrestricted demo logins created confusion; previous sessions leaked user conversations across login switches; human photos were used for testing personas.
- **Root Cause:** Chat conversations and messages were stored in `localStorage` under un-scoped keys (`pocketuni_chats`, `pocketuni_messages`). When switching accounts, existing state remained in memory.
- **Remediation:**
  - Implemented strict Three-Account Sandbox: **Super Admin Sandbox** (`utsavkumawat05@gmail.com`), **Student Sandbox** (`aarav.sharma@example.invalid`), and **Faculty Sandbox** (`dr.mausam.chouksey@mitsgwalior.in`).
  - Switched avatars to abstract geometric vector monograms (`SA`, `ST`, `FC`).
  - Scoped all client-side persistence per user ID (`pocketuni_chats_${currentUser.id}`, `pocketuni_messages_${currentUser.id}`, `pocketuni_applications_${currentUser.id}`).
  - Enforced ownership verification (`Conversation.user_id == current_user.id`) across all chat endpoints (`GET`, `POST`, `PATCH`, `DELETE`). Cross-user access returns strict `404 Not Found`.

### 11.3 Real-Time Synchronization via WebSockets (`/api/v1/ws`)
- **Defect:** State changes (application status transitions, faculty profile edits, announcements) required manual browser refresh.
- **Root Cause:** Missing active bidirectional push channel between backend PostgreSQL mutations and connected clients.
- **Remediation:**
  - Architected `RealtimeConnectionManager` in `backend/app/services/realtime_service.py` supporting user-directed and role-broadcast event distribution.
  - Added authenticated WebSocket endpoints at `/api/v1/ws` and `/ws` validating JWT bearer tokens via query parameters.
  - Created `src/services/realtimeClient.ts` with auto-reconnection, ping/pong heartbeats, and event listeners.
  - Connected real-time broadcast triggers to application status transitions (`application_status_changed`) and faculty profile updates (`faculty_profile_updated`).

### 11.4 Progressive Gemini Streaming & Free-Tier Quota Resilience
- **Defect:** AI assistant responses were buffered entirely or failed with uncaught exceptions when free-tier rate limits occurred.
- **Root Cause:** Chat endpoint only exposed blocking REST endpoints, and unhandled `429 RESOURCE_EXHAUSTED` errors from `google-genai` broke generation.
- **Remediation:**
  - Upgraded `/api/v1/chat/conversations/{conv_id}/stream` to full Server-Sent Events (SSE) streaming yielding citations, intent widgets, and progressive text deltas (`event: delta`).
  - Persisted user query and complete assistant answer to PostgreSQL after stream completion.
  - Added graceful rate-limit backoff and institutional notice fallback in `backend/app/services/gemini_service.py` ensuring grounded retrieved context is always presented even if the daily Gemini quota is exceeded.

### 11.5 Faculty Directory Enrichment & Multi-Department Filtering
- **Defect:** Faculty directory lacked complete data for Dr. Shradha Dubey, Dr. Aftab Ahmed Ansari, Prof. Ramnaresh Sharma, and department filtering was non-functional.
- **Root Cause:** Incomplete manual seed data; missing database columns for professional highlights and external scholarly links.
- **Remediation:**
  - Created Alembic migration `d4a9ef182390` adding `professional_highlights_json`, `external_links_json`, and `phone_internal` to `faculty_profiles`.
  - Built `backend/app/services/faculty_enrichment_service.py` parsing verified data from screenshots in `info/` and official web pages.
  - Ingested verified records: Dr. Shradha Dubey (CSE, 5 verified publications, pose estimation), Dr. Aftab Ahmed Ansari (IoT, 5 publications), Prof. Ramnaresh Sharma (CSE, merged duplicate OCR record, 4 publications), plus 9 CSE faculty and 5 IoT faculty.
  - Upgraded frontend `FacultyDirectoryView.tsx` with live multi-department filter (`All`, `CAI`, `CSE`, `IoT`).

### 11.6 Timetable Exact Period Slot Timings Discrepancy Resolved
- **Defect:** Discrepancy between slot timings (09:30–10:30 vs 10:00–11:00).
- **Proof & Resolution:** OCR audit on all three authoritative scanned master timetables (`III Sem`, `V Sem`, `VII Sem`, Session July–Dec 2026) confirmed the official schedule:
  - **Period 1:** 10:00 AM – 11:00 AM
  - **Period 2:** 11:00 AM – 12:00 PM
  - **Period 3:** 12:00 PM – 01:00 PM
  - **Lunch Break:** 01:00 PM – 02:00 PM
  - **Period 4:** 02:00 PM – 03:00 PM
  - **Period 5:** 03:00 PM – 04:00 PM
  - **Period 6:** 04:00 PM – 05:00 PM
- **Action:** Updated `SLOT_TIMINGS` in `timetable_service.py` and updated all 95 database `TimetableEntry` records to authoritative hours.

### 11.7 Timetable Unsafe Defaults Removal & Honest Availability Complement
- **Defect:** Generic queries defaulted silently to "AIR III Sem Sec A". Faculty availability marked all faculty not teaching as "free", claiming faculty without published timetables were available.
- **Remediation:**
  - Removed all silent fallbacks in `intent_router.py`. Unspecified branch/semester returns an honest clarification request. Queries for unsupported branches (e.g. Civil Engineering) return an honest notice indicating only CAI timetables are currently published.
  - Fixed `get_faculty_availability`: calculates complement strictly against `known_tt_faculty_names`. Faculty not appearing on published master timetables are categorized as `unknown_coverage_faculty` with explanatory status: *"Schedule not covered in currently published master timetables."*

### 11.8 Application Outbox Queue Security & Realistic Dispatch
- **Defect:** Fake simulated email relay claimed `"Simulated official SMTP relay"`. The outbox inspection route `/api/v1/applications/outbox/queue` lacked authorization checks.
- **Remediation:**
  - Restricted `/api/v1/applications/outbox/queue` strictly to Super Administrators (`require_super_admin`). Unauthenticated requests receive `401`, students and faculty receive `403`.
  - Replaced fake simulated dispatch with real institutional queue status (`"QUEUED"`).
  - Added support for `revision_requested` and `resubmitted` states with notification triggers.

### 11.9 Confidential Student Marks Protection
- **Defect:** Confidential internal assessment document (`2nd semester minor 2 Lab and theory marks.pdf`) was present in raw seed folders.
- **Remediation:**
  - Permanently removed physical file from workspace filesystem.
  - Appended `*marks*.pdf`, `*marks*.xlsx`, `*marks*.csv`, `*internal_marks*`, `*confidential*` to `.gitignore`.
  - Marked database document record as `is_deleted = True`, `status = 'RESTRICTED_CONFIDENTIAL'`, and deleted all associated chunks from PostgreSQL vector store.
  - Implemented strict server-side download block returning `403 Forbidden` for confidential/restricted records.

### 11.10 Student Discovery Privacy & Contact Protection
- **Defect:** Discovery results could expose demo profiles, private emails/phone numbers, or display the searching student to themselves.
- **Remediation:**
  - Added filter `User.is_demo == False` and `User.id != current_user.id` in `backend/app/api/v1/routes/students.py`.
  - Enforced explicit opt-in requirement (`p.visibility.is_public == True`).
  - Contact emails are only included if `p.visibility.show_contact == True`. Personal phone numbers are never returned in public cards.

### 11.11 Avatar Upload Validation & Institutional Vector Monograms
- **Defect:** Avatar upload accepted raw URLs without file validation or sanitization.
- **Remediation:**
  - Implemented voluntary avatar upload (`POST /me/avatar/upload`) with strict extension and MIME verification (`image/png`, `image/jpeg`, `image/webp`), 2MB size enforcement, and PIL image sanitization.
  - Added institutional SVG vector monogram badge generator (`rx="64"`, Burnt Copper ring, Deep Midnight background).
  - Implemented directory traversal defense with sanitized UUID filenames.

---

## 2. DESIGN & PALETTE TRANSFORMATION

The user interface was unified under the authoritative MITS institutional palette:

| Token | Name | Hex Code | Purpose |
|---|---|---|---|
| `midnight` | Deep Midnight | `#14252B` | Primary headings, dark accents, brand badge |
| `forest` | Forest Teal | `#176B68` | Secondary navigation, verified pills, icons |
| `porcelain` | Porcelain | `#F5F3EE` | Clean content surfaces, modals, background |
| `sand` | Warm Sand | `#E7DFD2` | Borders, subtle card dividers, neutral chip |
| `copper` | Burnt Copper | `#B96D47` | High-emphasis CTAs, interactive highlights |
| `sage` | Soft Sage | `#8A9B87` | Success badges, verified student indicators |
| `charcoal` | Charcoal | `#273238` | Body typography, secondary metadata |

---

## 3. AUTOMATED VERIFICATION RESULTS

- **Master Transformation Suite (`test_master_transformation.py`):** 20 passed / 20 tests (100% pass rate).
- **Frontend Build (`tsc && vite build`):** Clean build (0 errors, 1,612 modules transformed).
- **PostgreSQL Database:** Intact on port 5432 with 50 authoritative tables and active Alembic revision `d4a9ef182390`.
