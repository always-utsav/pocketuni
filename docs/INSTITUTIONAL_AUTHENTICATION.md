# Institutional Authentication & Identity Guide
## PocketUni — MITS Gwalior AI Platform

This document details the architecture, configuration, and security controls governing institutional authentication, Google OAuth 2.0 flow, and role-based access control within PocketUni.

---

## 1. Authentication Architecture Overview

PocketUni enforces strict multi-tenant institutional authentication. No guest accounts or anonymous access are permitted to student records, administrative panels, or restricted academic services.

```
+-------------------------------------------------------------+
|                   First-Screen Role Selector                |
|       [Super Administrator]      [Student]      [Faculty]   |
+-------------------------------------------------------------+
                               |
                               v
            GET /api/v1/auth/google/url?role={ROLE}
                               |
                               v
          +-----------------------------------------+
          |  Google OAuth 2.0 Consent Screen        |
          |  (accounts.google.com)                  |
          +-----------------------------------------+
                               | (code, state)
                               v
         POST /api/v1/auth/google/callback
                               |
      +------------------------+------------------------+
      | Verification Steps:                             |
      | 1. CSRF State match & TTL expiry                |
      | 2. Server-side code exchange via token endpoint |
      | 3. ID token signature & aud/iss/exp validation  |
      | 4. email_verified == True assertion             |
      | 5. Domain authorization according to role:       |
      |    - Super Admin: In explicit allowlist         |
      |    - Student: Must end with @mitsgwl.ac.in      |
      |    - Faculty: Must end with @mitsgwalior.in     |
      |    - Personal Gmail: Rejected unless allowlisted|
      | 6. Map / link google_sub to user record         |
      | 7. Create UserSession & log AuditEvent          |
      | 8. Issue signed RS256/HS256 JWT                 |
      +-------------------------------------------------+
```

---

## 2. Institutional Role Hierarchy & Domain Rules

| Role | Permitted Domains | Allowed Dashboards | Super Admin Allowlist Eligible |
|---|---|---|---|
| **Super Administrator** | Allowlisted Google emails (`utsavkumawat05@gmail.com`, `guptamahi0207@gmail.com`) | Super Admin Portal, Student Mode, Faculty Mode | Yes |
| **Student** | `@mitsgwl.ac.in`, `*.invalid` (dev only) | Student Chat, Applications, Profile | No |
| **Faculty** | `@mitsgwalior.in`, `*.invalid` (dev only) | Faculty Profile, Application Review, Mentorship | No |

### Error Messaging on Role Mismatch
If an authenticated user attempts to select an incompatible role (e.g., student logging in under Faculty role):
> *"Your account is not authorised to access this role. Please select your correct account type or contact the administrator."*

If a personal email (e.g. `@gmail.com`) attempts to log in under Student or Faculty role:
> *"Personal Google accounts cannot access PocketUni student or faculty dashboards. Please use your official MITS institutional account (@mitsgwl.ac.in or @mitsgwalior.in)."*

---

## 3. Super Admin Controlled Context Switching

Super Administrators possess institutional oversight across the entire product. To review the student or faculty experience without corrupting academic records:

1. Super Admin clicks the **Context Switcher** pill in the top navigation bar.
2. The frontend invokes `POST /api/v1/auth/context-switch`:
   ```json
   {
     "target_context": "STUDENT" // or "FACULTY" or "SUPER_ADMIN"
   }
   ```
3. The backend checks:
   - Requester is in `SUPER_ADMIN_ALLOWLIST` or holds the `SUPER_ADMIN` role.
   - Non-administrators attempting this endpoint receive `403 Forbidden`.
4. The system logs an immutable audit entry:
   ```json
   {
     "action": "CONTEXT_SWITCH",
     "actor_email": "utsavkumawat05@gmail.com",
     "change_summary": "Super Admin switched active dashboard context to STUDENT"
   }
   ```
5. A refreshed JWT is issued containing `active_context: "STUDENT"`.
6. **Zero Fabrication Guarantee:** The context switch does **not** create a dummy student record in `student_profiles` or a dummy faculty record in `faculty_profiles`.

---

## 4. Google OAuth 2.0 Client Configuration

For production deployment on local or institutional domains, register the following in **Google Cloud Console**:

- **Application Type:** Web application
- **Authorized JavaScript origins:**
  - `http://localhost:5173` (Vite dev server)
  - `http://localhost:3000` (Production preview)
- **Authorized redirect URIs:**
  - `http://localhost:5173/auth/callback` (Frontend SPA handler)
  - `http://localhost:8000/api/v1/auth/google/callback` (Direct backend handler)
- **Scopes:**
  - `openid`
  - `https://www.googleapis.com/auth/userinfo.email`
  - `https://www.googleapis.com/auth/userinfo.profile`

---

## 5. Security & CSRF Defenses

1. **State Token Generation:** Every login request creates a cryptographically secure 32-byte hex token stored in a server-side cache with a 10-minute TTL.
2. **One-Time Consumption:** Upon callback arrival, the state token is popped and invalidated immediately.
3. **Audience & Issuer Verification:** The backend verifies that `aud` strictly equals `settings.GOOGLE_CLIENT_ID` and `iss` is `accounts.google.com`.
4. **Google Subject Mapping:** The unique numeric ID (`google_sub`) returned by Google is recorded on the `users` table. If a user attempts to sign in with an email already bound to a different `google_sub`, the transaction is blocked to prevent account hijacking.
5. **Local Development Sandbox:** When Google credentials are unconfigured or local testing is required, developers may use the controlled `/api/v1/auth/dev-login` endpoint, clearly flagged with `[Local Dev Sandbox]` in the UI.
