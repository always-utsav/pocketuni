# PocketUni — Super Admin & Institutional Document Management Guide

## 1. Access & Security Guardrails
- **Super Admin Email:** `utsavkumawat05@gmail.com`
- **Role Requirement:** All `/api/v1/admin/*` and `/api/v1/documents/*` publication routes enforce strict role checks (`require_super_admin`). Unauthenticated or non-admin requests receive HTTP 401/403.
- **Audit Logging:** Every administrative action (document upload, classification change, publishing, unpublishing, marks reconciliation inspection) generates an immutable entry in the `audit_logs` table.

## 2. Super Admin Dashboard Features

### A. Document Library & Multi-Facet Filtering
The Super Admin dashboard provides library filtering across:
- **Category:** All 16 standardized institutional categories.
- **Workflow Status:** `UPLOADED`, `PROCESSING`, `NEEDS_REVIEW`, `READY_TO_PUBLISH`, `PUBLISHED`, `ARCHIVED`.
- **Semester:** Filter by semester (e.g., `III Semester`, `V Semester`, `VII Semester`).
- **Academic Year & Batch:** Filter by cohort years (e.g., `2025-26`, `2026-27`).

### B. Controlled Review & Publishing Modal
When inspecting an uploaded document, the review modal allows:
1. **Metadata Editing:** Modify category, academic year, semester, issuing authority, and effective dates.
2. **Target Audience Mapping:** Specify target scopes (e.g., Entire Institution, Centre for AI, Faculty Only, Students Only).
3. **Marks Reconciliation Preview:** For documents containing confidential marks, an isolated preview displays parsed student marks and reconciliation status while enforcing strict non-publication safeguards.
4. **Authoritative Publishing Toggle:** Mark documents as authoritative institutional sources. Once published, documents become eligible for downstream student discovery.

### C. Live Document Statistics
- Real-time counts of total documents, published materials, pending reviews, and extraction job status metrics.
