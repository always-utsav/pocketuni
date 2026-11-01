# Google OAuth 2.0 Setup & Integration Guide

## 1. Overview
PocketUni supports secure Google OAuth 2.0 single sign-on alongside local development credentials.

The authentication flow enforces:
- CSRF protection via cryptographically generated `state` parameters stored in secure cookies/cache.
- Verification via Google's `tokeninfo` endpoint (`https://oauth2.googleapis.com/tokeninfo`).
- Domain validation restricting access to official institutional accounts (`@mitsgwalior.in`) or configured Super Admin email allowlists.
- Super Admin auto-elevation for specified administrator emails (e.g., `utsavkumawat05@gmail.com`).

---

## 2. Google Cloud Console Configuration

To enable live Google OAuth in production or full staging environments:

1. **Access Google Cloud Console**:
   Navigate to [Google Cloud Console](https://console.cloud.google.com/) and create or select the `PocketUni` project.
2. **Configure OAuth Consent Screen**:
   - User Type: **External** (or **Internal** if configured within a Google Workspace domain).
   - App Name: `PocketUni - MITS AI Assistant`
   - User Support Email: your administrative email
   - Developer Contact Information: your administrative email
   - Scopes: `openid`, `https://www.googleapis.com/auth/userinfo.email`, `https://www.googleapis.com/auth/userinfo.profile`
3. **Create OAuth Client ID**:
   - Application Type: **Web application**
   - Name: `PocketUni Local & Production Client`
   - Authorized JavaScript origins:
     - `http://localhost:5173`
     - `http://127.0.0.1:5173`
     - `http://localhost:8000`
   - Authorized redirect URIs:
     - `http://localhost:5173/auth/callback`
     - `http://localhost:8000/api/v1/auth/google/callback`
4. **Copy Credentials**:
   Copy the generated `Client ID` and `Client Secret`.

---

## 3. Environment Variable Configuration

Update your `.env` (and `backend/.env`) file with the copied values:

```env
GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret-here"
GOOGLE_REDIRECT_URI="http://localhost:5173/auth/callback"
SUPER_ADMIN_EMAILS="utsavkumawat05@gmail.com,admin@mitsgwalior.in"
```

---

## 4. Operational Flow & Fallback Mode

1. **Configuration Status Inspection**:
   - Endpoint `GET /api/v1/auth/oauth-status` checks whether valid non-placeholder Google credentials exist.
   - If `configured: false`, the frontend gracefully displays the local development login switch (Student, Faculty, Super Admin) and provides an alert banner indicating Google OAuth is awaiting client credentials.
2. **Token Exchange & User Provisioning**:
   - Once redirected from Google with an `id_token` or `code`, the backend validates the token directly with Google.
   - If the user exists in PostgreSQL, their session JWT is issued.
   - If the user is new and matches an institutional domain or the super admin list, an account is automatically provisioned with the appropriate role.
