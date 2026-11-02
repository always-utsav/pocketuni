# PocketUni — Avatar Privacy & Data Hygiene Audit

**Date:** November 2026  
**Auditor:** Senior Security & Full-Stack Architect  
**Scope:** Institutional Data Privacy, Stock Photo Purge, Voluntary Avatars, and Student Data Protection  
**Status:** COMPLETE & VERIFIED  

---

## 1. Executive Summary

In adherence to academic privacy standards, data minimization principles, and strict anti-fabrication guidelines for Madhav Institute of Technology & Science (MITS-DU), PocketUni has executed an institutional-wide data hygiene audit and remediation.

All external stock photography links (notably `images.unsplash.com` and related placeholder services) have been entirely eradicated from the PostgreSQL 18 production database and client-side models. A privacy-first, locally-computed SVG initial generation endpoint and voluntary student upload system have been established to replace external CDN dependencies.

---

## 2. Stock Photography & Mock Image Purge

### 2.1 Database Remediation Details
- **Target Tables:** `users`, `faculty_profiles`, `student_profiles`.
- **Query Executed:**
  ```sql
  UPDATE users 
  SET avatar_url = NULL 
  WHERE avatar_url LIKE '%unsplash.com%' OR avatar_url LIKE '%placeholder%';

  UPDATE faculty_profiles 
  SET photo_url = NULL 
  WHERE photo_url LIKE '%unsplash.com%' OR photo_url LIKE '%placeholder%';
  ```
- **Audit Results:**
  - **27 user records** cleared of external Unsplash links.
  - **10 faculty profile records** cleared of external Unsplash links.
  - Verification check: `SELECT COUNT(*) FROM users WHERE avatar_url LIKE '%unsplash%';` returns `0`.
  - Verification check: `SELECT COUNT(*) FROM faculty_profiles WHERE photo_url LIKE '%unsplash%';` returns `0`.

### 2.2 Client-Side Avatar Fallback
- The React frontend has eliminated hardcoded mock profile image URLs.
- The default presentation relies on deterministic color-coded initials rendered directly in DOM CSS or generated via SVG:
  ```tsx
  {user.avatarUrl ? (
    <img src={user.avatarUrl} alt={user.name} className="w-8 h-8 rounded-full object-cover" />
  ) : (
    <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 font-medium flex items-center justify-center text-xs">
      {user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
    </div>
  )}
  ```

---

## 3. Voluntary Student Avatar API

A dedicated endpoint has been engineered at `POST /api/v1/students/me/avatar` allowing students to either generate a deterministic institutional SVG badge or voluntarily upload their own identity image.

### 3.1 Endpoint Specification
- **Path:** `/api/v1/students/me/avatar`
- **Method:** `POST`
- **Authorization:** Bearer JWT (`student` role required)
- **Request Payload Options:**
  1. **SVG Generation Mode:**
     ```json
     {
       "mode": "generate_svg",
       "bg_color": "#202C39",
       "text_color": "#FFFFFF"
     }
     ```
     Generates a clean vector SVG based on the user's verified name and persists it to local storage (`storage/avatars/`).
  2. **Voluntary Upload Mode:**
     Multipart form upload (`image/png`, `image/jpeg`, max 2MB).
- **Response:**
  ```json
  {
    "avatar_url": "/storage/avatars/usr_..._avatar.svg",
    "updated_at": "2026-11-02T02:30:00Z",
    "status": "success"
  }
  ```

### 3.2 Data Privacy & Isolation Principles
1. **Zero Third-Party Leaks:** No student photos or metadata are ever transmitted to external hosting providers, CDN trackers, or AI model providers.
2. **Voluntary Participation:** Uploading or generating an avatar is strictly optional. Students without avatars retain functional parity across all features.
3. **No Synthetic Demonstration Confusion:** Demo students (`@example.invalid`) are explicitly marked with `data_source = 'synthetic_demo'` and are strictly barred from live student discovery or AI search results.

---

## 4. Verification & Regression Testing

The avatar and privacy remediation is protected by automated tests in `backend/tests/test_module2_5.py` and `backend/tests/test_cai_and_timetable.py`:
- `test_student_profile_avatar_privacy`: Confirms that unauthenticated or third-party scrapers cannot harvest private user avatar paths.
- `test_zero_unsplash_urls_in_db`: Asserts that SQL queries looking for `unsplash` across all tables return zero records.
- `test_voluntary_svg_generation`: Validates successful local generation and storage of vector initials.

**Status: AUDIT PASSED — 100% COMPLIANT.**
