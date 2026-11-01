# PocketUni — Institutional Data Import & Seeding Guide

## 1. Directory Structure

```
data/
├── seed/
│   ├── incoming/                 # Original incoming PDFs & Word documents
│   │   ├── 2nd semester minor 2 Lab and theory marks.pdf
│   │   ├── Firsty_year_Induction_2025  .docx.pdf
│   │   ├── II Year Scheme admitted in session 2025-26.pdf
│   │   ├── II Year Syllabus admitted in session 2025-26.pdf
│   │   ├── III Year Syllabus session 2024-25.pdf
│   │   ├── III Sem TT July-Dec 2026.pdf
│   │   ├── V Sem TT July-Dec 2026.pdf
│   │   ├── VII Sem TT July-Dec 2026.pdf
│   │   └── Professional_Certification_Course_List.pdf
│   └── reference/                # Clean institutional JSON models & schema templates
├── storage/                      # Managed application upload storage
│   ├── documents/                # Stored institutional documents by UUID
│   └── temp/                     # Processing workspace for extraction jobs
```

## 2. Seed Execution

To seed the PostgreSQL database with the verified MITS Centre for AI faculty directory, synthetic demo students, academic calendars, timetables, and audit records:

```powershell
& .\backend\.venv\Scripts\python.exe .\backend\app\seed.py
```

### Seeding Entities:
1. **Super Admin User:** `utsavkumawat05@gmail.com` (Role: `SUPER_ADMIN`, verified institutional authority).
2. **22 Verified CAI Faculty:** Official faculty of MITS Centre for Artificial Intelligence, including Dr. Mausam Chouksey (Assistant Professor, Mentor assigned).
3. **4 Synthetic Demo Students:**
   - Aarav Sharma (`aarav.sharma@example.invalid`, Roll: `DEMO-BTAD24O101`)
   - Priya Patel (`priya.patel@example.invalid`, Roll: `DEMO-BTAD24O102`)
   - Rohan Gupta (`rohan.gupta@example.invalid`, Roll: `DEMO-BTAD24O103`)
   - Ananya Verma (`ananya.verma@example.invalid`, Roll: `DEMO-BTAD24O104`)
   All marked with `is_demo = True`.
4. **Academic Year & Semester Calendars:** 2026-27 Odd & Even Semester working calendars.
5. **Audience Taxonomy:** MITS institutional audience hierarchies (Campus, Faculty, Department, Semester).

## 3. Internal Marks Reconciliation Endpoint

For documents classified as `INTERNAL_MARKS`:
- Endpoint: `GET /api/v1/documents/{doc_id}/reconcile-marks`
- Access: `SUPER_ADMIN` only.
- Output: Structured list of extracted student enrollment records, course marks, and validation warnings for reconciliation against academic ERP tables without accidental publication to student portals.
