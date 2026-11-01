# Excel Synchronization & Atomic Persistence Guide
## PocketUni — MITS Gwalior AI Platform

This document describes the mechanics of the bidirectional synchronization engine connecting PostgreSQL 18 with local Excel workbooks.

---

## 1. Synchronization Architecture

```
+-------------------------------------------------------------+
|                         PostgreSQL 18                       |
|               (Authoritative Source of Truth)               |
+-------------------------------------------------------------+
         ^                                           |
         | 1. Transactional Import                   | 2. Profile Sync Trigger
         |    (via Admin UI)                         |    (Student/Faculty PUT)
         |                                           v
+------------------+                       +-------------------+
|  Roster Preview  |                       |   ExcelSyncJob    |
|   & Validation   |                       |   (Queued Job)    |
+------------------+                       +-------------------+
         ^                                           |
         |                                           v
+-------------------------------------------------------------+
|                  excel_service.sync_user_profile()          |
|  - Open Workbook                                            |
|  - Find matching row by institutional_email or ID           |
|  - Update row attributes                                    |
|  - Write to temp file: /tmp/temp_pocketuni_students.xlsx    |
|  - Atomic replace: shutil.move(temp, target)                |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|               Local Authoritative Workbooks                 |
|             (pocketuni_students.xlsx in root)               |
|             (pocketuni_faculty.xlsx in root)                |
+-------------------------------------------------------------+
```

---

## 2. Atomic Write Guarantee & Crash Resistance

To prevent file corruption during simultaneous edits or server interruptions:
1. Workbooks are **never** written directly in-place.
2. The openpyxl engine saves the workbook to an isolated operating system temporary file:
   ```python
   temp_dir = tempfile.gettempdir()
   temp_file = os.path.join(temp_dir, f"temp_{os.path.basename(target_path)}")
   wb.save(temp_file)
   ```
3. Once the serialization successfully completes without exception, an atomic filesystem move overwrites the target file:
   ```python
   shutil.move(temp_file, target_path)
   ```
4. If an unhandled exception or crash occurs during serialization, the existing master workbook remains pristine and uncorrupted.

---

## 3. Duplicate Key Resolution & Roster Reconciliation

When importing an uploaded workbook:
1. **Primary Key Match:** The importer first matches incoming rows against existing users by `institutional_email`.
2. **Secondary Match (Students):** Matches by `roll_number` or `enrolment_number`.
3. **Secondary Match (Faculty):** Matches by `faculty_identifier`.
4. **Behavior on Match:** If the user exists, fixed institutional fields and existing relations are updated transactionally. If the user does not exist, a new `User` record and linked profile shell are created.
5. **Batch Audit Record:** Every import creates a `RosterImportBatch` record in PostgreSQL containing:
   - `total_records`: Number of rows processed.
   - `created_records`: Count of newly provisioned users.
   - `updated_records`: Count of existing users updated.
   - `errors_summary`: Detailed array of row numbers and validation failure explanations.

---

## 4. Background Sync Job Lifecycle (`excel_sync_jobs`)

When a student or faculty member updates their profile via self-service APIs:
1. The API transactionally commits the changes to PostgreSQL.
2. A job record is created in `excel_sync_jobs` with status `PENDING`.
3. The sync worker executes `excel_service.sync_user_profile(db, user_id)`:
   - Sets status to `PROCESSING`.
   - Locates the student's row in `pocketuni_students.xlsx` (or faculty in `pocketuni_faculty.xlsx`).
   - Updates `bio`, `skills`, `projects`, `updated_at`, etc.
   - Saves via atomic tempfile replacement.
   - Updates job status to `COMPLETED` with `completed_at` timestamp.
4. If an error occurs, the job status is set to `FAILED`, the error message is recorded, and the PostgreSQL record remains fully intact.
