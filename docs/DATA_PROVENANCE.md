# Data Provenance & Synthetic Data Isolation Policy
## PocketUni — MITS Gwalior AI Platform

This document establishes the official data classification, provenance tracking, and synthetic record isolation rules enforced across PocketUni.

---

## 1. Core Principles of Data Provenance

To safeguard institutional credibility and comply with academic integrity standards:
1. **Zero Falsification:** PocketUni **never** creates fabricated student records and represents them as official university data.
2. **Clear Provenance Tagging:** Every record in the database and Excel workbooks carries an explicit `data_source` and `is_demo` tag.
3. **Audit Trail Accountability:** Any administrative creation, modification, or import records the actor ID, source filename, and timestamp.

---

## 2. Data Categories & Provenance Markers

| Category | Typical Records | Provenance Marker (`data_source`) | `is_demo` Flag | Grounding Status |
|---|---|:---:|:---:|---|
| **Official Institutional Documents** | 9 MITS academic PDFs (Syllabus, Schemes, Induction, Timetables, Certifications) | `mits_official_pdf` | `FALSE` | **100% Grounded** in verified institution files. |
| **Live Crawled Web Data** | CAI overview, regulations from `web.mitsgwalior.in` | `mits_web_crawled` | `FALSE` | **100% Grounded** with live source URLs. |
| **Synthetic Demo Students** | Exactly 10 demo records in `pocketuni_students.xlsx` | `synthetic_demo` | `TRUE` | **Simulated Demo Data** (DEMO- roll numbers, .invalid domains). |
| **Synthetic Demo Faculty** | Demo records in `pocketuni_faculty.xlsx` | `synthetic_demo` | `TRUE` | **Simulated Demo Data** (.invalid domains). |
| **Official Centre for AI Faculty** | 22 real CAI faculty members (Dr. Manish Dixit, Dr. Mausam Chouksey, etc.) | `mits_official_cai_faculty` | `FALSE` | **Verified Faculty** from official institutional directory. |
| **Confidential Internal Marks** | 2nd Semester Minor 2 theory & lab marks | `mits_sensitive_marks_restricted` | `FALSE` | **Restricted Isolation:** NEVER chunked into RAG vector repository. |

---

## 3. Synthetic Student Isolation Standards (Section 10 Compliance)

To guarantee that demo students cannot be mistaken for registered students:
1. **Fictional Names:** Aarav Sharma, Mahi Gupta, Rohan Shrivastava, Priya Patel, Devansh Joshi, Ananya Deshmukh, Kabir Mehta, Ishaan Verma, Yash Choudhary, Sneha Kulkarni.
2. **Reserved RFC 2606 Domains:** All email addresses use the reserved top-level domain `.invalid` (e.g. `demo.aarav.sharma@example.invalid`).
3. **Prefix Constraint:** All synthetic student roll numbers begin with the prefix `DEMO-` (e.g. `DEMO-0901AI231001`).
4. **Boolean Flag:** The column `is_demo` is set to `TRUE` in both PostgreSQL and Excel.

---

## 4. Sensitive Internal Marks Confidentiality

The document `2nd_semester_minor_2_Lab_and_theory_marks.pdf` contains confidential student evaluation data.
- **Strict Privacy Rule:** This file was extracted into the relational tables `result_records` and `result_subjects` for individual student score retrieval.
- **RAG Vector Isolation:** Internal marks documents are **completely excluded** from `document_chunks`. Vector queries can never expose student marks to peers or unauthorized search prompts.
- **Verified by Automated Test:** `test_document_chunks_indexed_in_postgres` programmatically confirms that chunks with category `INTERNAL_MARKS` equal exactly **0**.
