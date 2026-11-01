# Institutional Roster & Excel Management Guide
## PocketUni — MITS Gwalior AI Platform

This guide outlines the structure, schemas, import validation, and synchronization workflows for student and faculty rosters in PocketUni.

---

## 1. Master Data Philosophy & Provenance

In PocketUni, **PostgreSQL 18 is the single authoritative source of truth** for all identity, academic credentials, and profile records.

Local Excel workbooks (`pocketuni_students.xlsx`, `pocketuni_faculty.xlsx`) located in the project root serve as:
1. **Master Institutional Roster Templates:** For administrative batch onboarding and offline maintenance.
2. **Synchronized Master Mirrors:** Automatically updated upon self-service profile updates or administrative alterations.
3. **Downloadable Offline Snapshots:** Downloadable by Super Admins on demand.

---

## 2. Student Master Roster Schema (`pocketuni_students.xlsx`)

The student workbook consists of **31 canonical columns**:

| Column Name | Type | Required | Description | Example |
|---|---|:---:|---|---|
| `institutional_email` | String | **Yes** | Official institutional Google address | `demo.aarav.sharma@example.invalid` |
| `google_subject_id` | String | No | Numeric Google Sub ID | `1092384712093847` |
| `full_name` | String | **Yes** | Student's official full name | `Aarav Sharma` |
| `roll_number` | String | **Yes** | Unique institutional roll number | `DEMO-0901AI231001` |
| `enrolment_number` | String | No | University enrolment number | `0901AI231001` |
| `department` | String | **Yes** | Academic department | `Centre for Artificial Intelligence` |
| `programme` | String | **Yes** | Academic programme | `B.Tech` |
| `branch` | String | **Yes** | Branch of study | `Artificial Intelligence and Machine Learning` |
| `specialization` | String | No | Track / specialization | `Deep Learning & Edge Computing` |
| `batch` | String | **Yes** | Academic batch range | `2023-2027` |
| `academic_year` | String | **Yes** | Current academic session | `2026-2027` |
| `semester` | Integer | **Yes** | Current semester number (1-8) | `5` |
| `section` | String | No | Section identifier | `A` |
| `date_of_admission` | Date/Str | No | Admission date (YYYY-MM-DD) | `2023-08-16` |
| `profile_picture` | URL | No | Avatar image URL | `https://images.unsplash.com/...` |
| `bio` | Text | No | Professional / academic biography | `Third-year AI undergraduate...` |
| `skills` | Comma-list | No | Comma-separated technical skills | `Python, PyTorch, C++, ROS` |
| `interests` | Comma-list | No | Academic interests | `Robotics, Generative Vision` |
| `projects` | JSON Array | No | Portfolio projects | `[{"title": "Rover", "description": "..."}]` |
| `achievements` | JSON Array | No | Awards / recognitions | `["Smart India Hackathon Finalist"]` |
| `certifications` | JSON Array | No | Professional certificates | `["DeepLearning.AI Specialist"]` |
| `experience` | JSON Array | No | Internships / club roles | `[{"role": "Lab Lead", "duration": "..."}]` |
| `resume` | URL | No | PDF link / storage path | `https://pocketuni.../resume.pdf` |
| `LinkedIn` | URL | No | LinkedIn profile URL | `https://linkedin.com/in/...` |
| `GitHub` | URL | No | GitHub profile URL | `https://github.com/...` |
| `portfolio` | URL | No | Personal site URL | `https://aarav-sharma.demo.invalid` |
| `profile_visibility` | String | No | `PUBLIC` or `PRIVATE` | `PUBLIC` |
| `created_at` | ISO-Date | No | Record creation timestamp | `2026-08-01T09:00:00Z` |
| `updated_at` | ISO-Date | No | Record update timestamp | `2026-10-15T12:00:00Z` |
| `is_demo` | Boolean | **Yes** | Flag indicating synthetic data | `TRUE` |
| `data_source` | String | **Yes** | Source provenance | `synthetic_demo` or `official_roster` |

---

## 3. Faculty Master Roster Schema (`pocketuni_faculty.xlsx`)

The faculty workbook consists of **23 canonical columns**:

| Column Name | Type | Required | Description | Example |
|---|---|:---:|---|---|
| `institutional_email` | String | **Yes** | Official institutional Google address | `demo.manish.dixit@example.invalid` |
| `google_subject_id` | String | No | Google Sub ID | `1092384712093848` |
| `faculty_identifier` | String | **Yes** | Unique faculty employee code | `FAC-CAI-001` |
| `full_name` | String | **Yes** | Official full name | `Dr. Manish Dixit` |
| `designation` | String | **Yes** | Official post | `Professor & Head` |
| `department` | String | **Yes** | Academic department | `Centre for Artificial Intelligence` |
| `centre` | String | No | Research centre | `Centre for Artificial Intelligence` |
| `official_profile_url`| URL | No | MITS portal web profile URL | `https://web.mitsgwalior.in/faculty/manish-dixit` |
| `research_interests` | Comma-list | No | Research areas | `Medical Image Analysis, Deep Learning` |
| `office_location` | String | No | Physical cabin location | `CAI Block, Room 204` |
| `office_hours` | String | No | Consultation availability | `Mon, Wed 14:00 - 16:00` |
| `bio` | Text | No | Academic / research summary | `Head of Centre for AI at MITS Gwalior...` |
| `qualifications` | String | No | Highest degrees | `Ph.D. (Computer Science), M.Tech` |
| `expertise` | Comma-list | No | Domain proficiencies | `Computer Vision, AI Governance` |
| `publications` | JSON Array | No | Key publications | `[{"title": "Deep Learning...", "year": 2025}]` |
| `courses` | JSON Array | No | Current teaching courses | `["Advanced Machine Learning", "Neural Networks"]`|
| `projects` | JSON Array | No | Research grants / projects | `[{"title": "AI for Healthcare", "agency": "DST"}]`|
| `profile_picture` | URL | No | Photo URL | `https://images.unsplash.com/...` |
| `profile_visibility` | String | No | `PUBLIC` or `PRIVATE` | `PUBLIC` |
| `created_at` | ISO-Date | No | Creation timestamp | `2026-08-01T09:00:00Z` |
| `updated_at` | ISO-Date | No | Last update timestamp | `2026-10-15T12:00:00Z` |
| `is_demo` | Boolean | **Yes** | Synthetic demo flag | `TRUE` |
| `data_source` | String | **Yes** | Provenance marker | `mits_web_crawled` or `synthetic_demo` |

---

## 4. Roster Onboarding & Import Lifecycle

1. **Pre-Validation (`POST /api/v1/admin/roster/preview`):**
   - The Super Admin uploads an `.xlsx` workbook.
   - The engine parses columns against `STUDENT_COLUMNS` or `FACULTY_COLUMNS`.
   - Checks for required fields: email, full name, roll number / faculty code, department.
   - Verifies duplicate keys within the uploaded file itself.
   - Identifies whether incoming rows match existing database users (flags for update vs. creation).
   - Generates a preview payload showing valid rows, invalid rows, and actionable error summaries.

2. **Transactional Commit (`POST /api/v1/admin/roster/import`):**
   - All rows are processed inside an atomic database transaction.
   - New users are created with pre-assigned roles (`STUDENT` or `FACULTY`).
   - Profile shells (`StudentProfile` or `FacultyProfile`) are attached.
   - Skills, projects, and research interests are parsed and normalized into relational tables.
   - A `RosterImportBatch` record is written to document the batch ID, filename, created count, updated count, and errors.
   - An immutable event is emitted to `audit_logs`.
   - The authoritative workbook in root is re-exported atomically to keep the disk mirror synchronized.

---

## 5. Administrative Roster Actions

Within Tab 16 of the Super Admin Portal:
- **Download Official Workbooks:** One-click authenticated download of `pocketuni_students.xlsx` and `pocketuni_faculty.xlsx`.
- **Edit Locked Institutional Fields:** Super Admin can adjust a student's semester, section, branch, or batch without requiring database SQL commands.
- **Account Status Toggling:** Super Admin can deactivate an account (preventing login while preserving academic records).
