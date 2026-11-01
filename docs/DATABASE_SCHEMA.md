# PocketUni Database Schema Reference (SQLAlchemy 2 / PostgreSQL)

The database schema consists of 50 tables organized into cohesive domains. All tables inherit common metadata: UUID primary key (`id`), timestamps (`created_at`, `updated_at`), soft-deletion flag (`is_deleted`), and synthetic flag (`is_demo`).

---

## 1. Domain Overview

### Identity & Authentication
* **`roles`**: System roles (`SUPER_ADMIN`, `FACULTY`, `STUDENT`).
* **`users`**: User identity accounts, roll numbers, department associations, and active states.
* **`user_roles`**: Many-to-many relationship mapping users to roles.
* **`authentication_accounts`**: Federated provider mapping (`google`, `local_dev`).
* **`user_sessions`**: Session metadata and token tracking.

### Academic Hierarchy
* **`institutions`**: University definition (e.g. Madhav Institute of Technology & Science, code `MITS`).
* **`departments`**: Academic units (e.g. Centre for Artificial Intelligence, code `CAI`).
* **`programmes`**: Degrees offered (`B.Tech`, `M.Tech`).
* **`branches`**: Specializations (`B.Tech IT (AI & Robotics)`, `B.Tech AI & Machine Learning`, etc.).
* **`academic_years`**: Academic calendar years (`2026-2027`).
* **`semesters`**: Semester levels and term cycles.
* **`batches`**: Student graduation batches.

### Student Domain
* **`student_profiles`**: Extended student bios, portfolio links, collaboration preferences, and hackathon availability.
* **`skills`**: Master list of technical skills and categories.
* **`student_skills`**: Student proficiency mappings (`Beginner`, `Intermediate`, `Advanced`).
* **`projects`**: Student showcased projects with repositories and tech stacks.
* **`resume_metadata`**: Uploaded resume file details, SHA-256 hash digests, and file paths.
* **`profile_visibility`**: Public discovery flags and privacy controls.

### Faculty Domain
* **`faculty_profiles`**: Official faculty records, designations, department affiliations, office hours, and mentor tags.
* **`faculty_research_interests`**: Areas of specialization.
* **`faculty_education`**: Academic degrees and institutions.
* **`faculty_experience`**: Professional academic and administrative experience.
* **`faculty_publications`**: Research papers, journal titles, publication years, and DOIs.
* **`faculty_sources`**: Crawl metadata, retrieval timestamps, and source URLs.

### Institutional Document Management
* **`institutional_documents`**: Core document records, file extensions, SHA-256 hashes, status, and academic metadata.
* **`document_versions`**: Historical revision history and change summaries.
* **`document_audiences`**: Audience targeting rules (`ENTIRE_INSTITUTION`, `CENTRE_FOR_AI`, `BRANCH`, etc.).
* **`document_extraction_jobs`**: Job status, processed page count, detected table counts, and execution metrics.
* **`extracted_document_contents`**: Paragraph-level text with page indices, headings, and classification types.
* **`extracted_tables`**: Structured multi-column tables with headers, rows, and cell coordinates.
* **`document_publication_histories`**: Publication and archival audit trails.
* **`document_sources`**: External source links and verification statuses.

### Academic Records & Examination
* **`timetable_entries`**: Scheduled lecture slots, timings, room assignments, faculty in-charge, and semesters.
* **`examination_entries`**: Datesheet rows, exam types (Mid-Term, End-Semester), dates, and timings.
* **`academic_calendar_entries`**: Academic year milestones, start/end dates, and applicable cohorts.
* **`result_records`**: Student semester SGPA/CGPA, examination sessions, and pass statuses.
* **`result_subjects`**: Subject-wise credits, marks obtained, maximum marks, and letter grades.

### Applications & Communication
* **`applications`**: Student submitted applications (leave, bonafide, permission, NOC).
* **`application_versions`**: Iterative revisions of application content.
* **`application_status_history`**: Audit trail of application transitions (draft, sent, approved, rejected).
* **`application_shares`**: Application sharing between students and faculty.
* **`application_documents`**: Supporting attachments for applications.
* **`conversations`**: College assistant chat threads.
* **`messages`**: Individual user and assistant messages with source grounding and feedback.
* **`notifications`**: Targeted notifications.
* **`feedback`**: User feedback ratings and comments.

### Administration & Audit
* **`audit_logs`**: Immutable, tamper-evident action logs with actor details and change summaries.
* **`admin_configurations`**: Dynamic institutional configuration flags.
* **`import_jobs`**: Batch import job tracking for CSV/XLSX imports.
* **`import_errors`**: Row-level validation failure logs.
