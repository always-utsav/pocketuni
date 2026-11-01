# PocketUni — Module 2 Architecture Specification
**Subsystem:** AI Intelligence, Institutional RAG, Application Automation & Workflows  
**Institution:** Madhav Institute of Technology & Science (MITS), Gwalior  

---

## 1. System Overview

Module 2 transforms PocketUni from an administrative database foundation into an intelligent, grounded, and role-governed university platform. The architecture integrates official Google Gemini models (`gemini-2.5-flash` for synthesis and reasoning; `gemini-embedding-001` with 3072 dimensions for dense retrieval) with PostgreSQL 18.

```
                      +---------------------------------------+
                      |       PocketUni React 18 Client       |
                      |   (ChatView, AppAgent, Discovery, UI) |
                      +-------------------+-------------------+
                                          |
                                HTTP / REST & SSE
                                          |
                      +-------------------v-------------------+
                      |      FastAPI Backend Engine (v1)      |
                      +-------------------+-------------------+
                                          |
     +-------------------+----------------+-------------------+-------------------+
     |                   |                |                   |                   |
+----v-----+       +-----v----+     +-----v-----+       +-----v----+        +-----v-----+
| Gemini   |       | RAG      |     | App Agent |       | Student  |        | Google    |
| Service  |       | Hybrid   |     | Workflow  |       | Discovery|        | OAuth     |
| (Client) |       | Engine   |     | & DOCX    |       | Engine   |        | Service   |
+----+-----+       +-----+----+     +-----+-----+       +-----+----+        +-----+-----+
     |                   |                |                   |                   |
+----v-----+       +-----v----------------v-------------------v----+              |
| Google   |       |            PostgreSQL 18 Database             |              |
| Gemini   |       |  - 52 Public Tables (inc. document_chunks)    |              |
| REST API |       |  - Hybrid Vector Storage (3072-dim embeddings)|              |
+----------+       +-----------------------------------------------+              |
                                          ^                                       |
                                          +---------------------------------------+
```

---

## 2. Key Components

### A. Centralised Gemini Service (`backend/app/services/gemini_service.py`)
- Standardized client wrapper around official Google `genai.Client`.
- Chat Model: `gemini-2.5-flash` (low-latency grounded synthesis, anti-injection system prompt).
- Embedding Model: `gemini-embedding-001` (3072-dimensional semantic embeddings).
- Built-in exponential backoff retry for transient network and rate-limit errors (HTTP 429).
- Secret protection: API keys remain server-side; diagnostics endpoints reveal only model identifiers and health status.

### B. Institutional Hybrid RAG Engine (`backend/app/services/rag_service.py`)
- Pre-retrieval role and academic scope enforcement in SQL before model prompt creation.
- Density: Cosine similarity over normalized 3072-dimensional chunk embeddings.
- Lexical: Token overlap against source sections and text blocks.
- Fusion: Reciprocal Rank Fusion ($Score = 0.75 \times Dense + 0.25 \times Lexical$).
- Strict document versioning and status checking: excludes `DRAFT`, `SUPERSEDED`, `ARCHIVED`, and `INTERNAL_MARKS`.

### C. Conversational Application Agent (`backend/app/services/application_agent_service.py`)
- Natural-language slot collection (application type, dates, reason, recipient).
- Verified student profile prefill (name, enrollment number, branch, semester) from database.
- Formal Indian academic formatting generation.
- Production `.docx` generation via `python-docx` stored in `storage/application_documents/`.
- Multi-state workflow: `draft` -> `sent` -> `approved` / `rejected` / `returned_for_correction`.

### D. Database-Backed Student Discovery (`backend/app/services/discovery_service.py`)
- Dynamic querying over `student_profiles`, `student_skills`, and `projects`.
- Explainable matching: highlights matching tags, skills, and projects.
- Privacy guard: filters out requesting student, enforces `is_public` and `show_contact` visibility flags, never displays marks or confidential data.

### E. Google OAuth Architecture (`backend/app/services/oauth_service.py`)
- Cryptographic state parameter verification to prevent CSRF.
- Server-side ID token validation with Google OAuth endpoints.
- Role resolution through institutional domain rules and strict Super Admin allowlist (`utsavkumawat05@gmail.com`).
