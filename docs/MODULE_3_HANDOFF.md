# Module 3 Handoff Specification
## PocketUni — MITS Gwalior AI Platform

**Author:** Lead AI & Full-Stack Architect  
**Handoff Date:** November 2026  
**Status:** **Module 1, 2, and 2.5 Fully Verified & Operationally Ready**

---

## 1. Baseline System State

All foundational and pre-deployment modules are complete. The project is running cleanly on Windows in a local environment:

- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide React.
  - Builds cleanly with `npm run build` (**0 TypeScript or Vite compilation errors**).
- **Backend:** FastAPI, SQLAlchemy 2, Alembic, Pydantic, Python 3.11.
  - Runs cleanly with Uvicorn on `http://localhost:8000`.
- **Database:** PostgreSQL 18.6 running locally on port 5432 (`pocketuni`).
  - **59 public tables** managed by Alembic revisions through `f45e46a94da4`.
  - **411 indexed vector chunks** in `document_chunks` (3072-dim embeddings).
- **Test Suite:** **40 Passed, 0 Failed, 0 Regressions** (`test_backend.py`, `test_module2.py`, `test_module2_5.py`).
- **Master Excel Workbooks:** `pocketuni_students.xlsx` (10 synthetic students) and `pocketuni_faculty.xlsx` in repository root.

---

## 2. Completed Capabilities Delivered in Module 2.5

1. **First-Screen Institutional Role Selector:** Clean entry screen requiring users to choose Super Admin, Student, or Faculty.
2. **Google OAuth 2.0 Identity Enforcement:**
   - Super Admin: Explicit allowlist (`utsavkumawat05@gmail.com`, `guptamahi0207@gmail.com`).
   - Students: Verified Google accounts ending with `@mitsgwl.ac.in`.
   - Faculty: Verified Google accounts ending with `@mitsgwalior.in`.
   - Personal emails rejected with explicit institutional guidance.
3. **Super Admin Context Switching:** Super Admins can switch between Super Admin Portal, Student Mode, and Faculty Mode with full audit logging and zero data fabrication.
4. **Master Data & Excel Synchronization:** Bidirectional sync between PostgreSQL and Excel workbooks with atomic tempfile replacement and preview/import/export endpoints.
5. **Locked Academic Profile Badges:** Fixed institutional fields (roll number, semester, designation) locked against self-service modifications and displayed with verified badges.
6. **MITS Web Ecosystem Crawler & E-Governance Directory:** Polite crawler for `web.mitsgwalior.in` and `ams.mitsgwalior.in` with SSRF firewall and vector search grounding.

---

## 3. Scope Boundaries & What NOT to Do Before Module 3

As per project guidelines:
- **Do NOT implement Docker or containerized deployment yet.**
- **Do NOT deploy to AWS, GCP, Vercel, or cloud databases yet.**
- **Do NOT configure cloud CI/CD pipelines yet.**
- These tasks belong strictly to **Module 3: Deployment, Containerization & Production Operations**.

---

## 4. Module 3 Preparation Checklist

When the user initiates Module 3, the incoming engineer should proceed with:
1. **Containerization (Docker & Compose):**
   - Multi-stage Dockerfile for FastAPI backend with Python 3.11 slim.
   - Multi-stage Dockerfile for React frontend (Vite build -> Nginx alpine).
   - `docker-compose.yml` orchestrating FastAPI, Nginx, and PostgreSQL 18.
2. **Environment Variable & Secret Management:**
   - Secret injection via container environment or orchestration secrets.
   - Database migrations auto-running on container startup (`alembic upgrade head`).
3. **Production Reverse Proxy & SSL Configuration:**
   - Nginx routing `/api/v1` to FastAPI and `/` to static frontend build.
   - SSL/TLS certificate handling and security headers.
4. **Health Check Probes:**
   - Integration with `/api/health` for container readiness and liveness probes.
