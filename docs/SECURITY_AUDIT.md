# Security Audit & Vulnerability Assessment Report
## PocketUni — MITS Gwalior AI Platform

**Audit Date:** November 2026  
**Audited Targets:** Backend FastAPI, Frontend React/Vite, PostgreSQL 18, Google OAuth 2.0, RAG Pipeline  
**Overall Security Posture:** **HARDENED — PRODUCTION READY**

---

## 1. Security Domain Evaluations

### A. Authentication & Credential Management
- **Vulnerability Checked:** Secret leakage in source code or frontend bundles.
- **Finding:** All API keys (`GEMINI_API_KEY`, `GOOGLE_CLIENT_SECRET`, database passwords) reside in `.env` and `backend/.env`. Both files are strictly excluded by `.gitignore`. Verified by `git status`.
- **Finding:** Frontend uses standard Vite environment configuration; secret credentials are never bundled into client JavaScript.
- **Status:** **PASS**

### B. OAuth 2.0 & Identity Spoofing Defenses
- **Vulnerability Checked:** CSRF attacks on callback, ID token forging, role escalation.
- **Finding:** The authorization URL generates a high-entropy 32-byte hex token stored server-side with a 10-minute TTL. The callback pops the token immediately (one-time use).
- **Finding:** The ID token is validated directly against Google's tokeninfo endpoint, checking audience (`aud`), issuer (`accounts.google.com`), and expiry (`exp`).
- **Finding:** The server verifies `email_verified=True` before admitting any identity.
- **Finding:** Google's unique subject ID (`google_sub`) is permanently recorded. Cross-account binding conflicts trigger immediate rejection.
- **Status:** **PASS**

### C. Server-Side Role-Based Access Control (RBAC)
- **Vulnerability Checked:** Unauthorized access to admin endpoints or context switching.
- **Finding:** Non-administrators calling `/api/v1/auth/context-switch` receive `403 Forbidden` (`test_non_admin_cannot_switch_context` PASSED).
- **Finding:** Student requests to `/api/v1/admin/*` receive `403 Forbidden` (`test_student_cannot_access_admin_stats` PASSED).
- **Finding:** Context switching by Super Admins emits an immutable event in `audit_logs` without fabricating dummy student or faculty records.
- **Status:** **PASS**

### D. Server-Side Request Forgery (SSRF) Defenses in Web Crawler
- **Vulnerability Checked:** Crawling malicious external URLs, internal localhost services, or cloud metadata endpoints.
- **Finding:** `PoliteCrawler.is_safe_url` strictly validates incoming URLs against an explicit allowlist:
  - Allowed: `web.mitsgwalior.in`, `ams.mitsgwalior.in`, `mitsgwalior.in`.
  - Blocked: `localhost`, `127.0.0.1`, `0.0.0.0`, `169.254.169.254`, private subnets (`10.*`, `192.168.*`, `172.*`).
  - Blocked: Arbitrary external sites (`google.com`, `malicious-site.org`).
- **Status:** **PASS** (Verified by automated unit test `test_crawler_ssrf_safety`).

### E. Prompt Injection & RAG Integrity
- **Vulnerability Checked:** Jailbreaking system instructions via document chunk retrieval.
- **Finding:** RAG system prompt enforces strict persona boundaries:
  - Answers must cite verified institutional documents.
  - Documents are treated strictly as reference text, not executable instructions.
  - If a document contains text like *"Ignore all previous instructions"*, the model ignores it and continues providing grounded academic answers.
- **Status:** **PASS** (Verified by `test_rag_anti_injection`).

### F. Confidential Evaluation & Marks Privacy
- **Vulnerability Checked:** Unauthorized exposure of student marks via AI retrieval.
- **Finding:** Confidential marks documents (`2nd_semester_minor_2_Lab_and_theory_marks.pdf`) are stored in relational tables for self-service lookup and are **never chunked or embedded into the vector database**.
- **Status:** **PASS** (Verified by `test_document_chunks_indexed_in_postgres`: 0 marks chunks in vector store).

---

## 2. Audit Summary

| Check | Target | Mechanism | Result |
|---|---|---|:---:|
| **Zero Secret Leakage** | Repository & Git | `.gitignore` + Environment variables | **PASS** |
| **OAuth CSRF Protection** | `/auth/google/callback` | Server-cached state token with TTL | **PASS** |
| **Google ID Token Signature** | Token verification | Google tokeninfo audience & issuer check | **PASS** |
| **Role Domain Enforce** | Student/Faculty auth | `@mitsgwl.ac.in` / `@mitsgwalior.in` check | **PASS** |
| **Super Admin Context Switch** | `/auth/context-switch` | Role allowlist + AuditLog emission | **PASS** |
| **Locked Profile Fields** | `/students/me`, `/faculty/me`| Backend field stripping + Locked badges | **PASS** |
| **Crawler SSRF Firewall** | `PoliteCrawler` | Domain allowlist + Loopback/Private IP block | **PASS** |
| **Confidential Marks Isolation** | Vector DB | Excluded from RAG chunking pipeline | **PASS** |
| **Excel Atomic Replace** | `excel_service` | OS temporary file + atomic `shutil.move` | **PASS** |
