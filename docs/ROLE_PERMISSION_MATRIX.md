# Role & Permission Matrix
## PocketUni — MITS Gwalior AI Platform

This document specifies the exact authorization boundaries, endpoint access, and field-level permissions for all user roles within PocketUni.

---

## 1. System Roles Overview

| Role Identifier | Description | Identity Verification Source |
|---|---|---|
| **SUPER_ADMIN** | Institutional oversight, system settings, document extraction, roster imports, crawler management. | Explicit server-side allowlist (`utsavkumawat05@gmail.com`, `guptamahi0207@gmail.com`). |
| **FACULTY** | Departmental teaching staff, mentors, application approvers, research profiles. | Google OAuth (`@mitsgwalior.in`) + Roster presence. |
| **STUDENT** | Undergraduate / Postgraduate students, applicants, team finders. | Google OAuth (`@mitsgwl.ac.in`) + Roster presence. |
| **PUBLIC** | Unauthenticated visitors. | None. Restricted strictly to landing page role selection. |

---

## 2. Endpoint Authorization Matrix

| Category | Endpoint | Method | Super Admin | Faculty | Student | Public |
|---|---|---|:---:|:---:|:---:|:---:|
| **Auth** | `/auth/google/url` | GET | Allowed | Allowed | Allowed | Allowed |
| | `/auth/google/callback` | POST | Allowed | Allowed | Allowed | Allowed |
| | `/auth/me` | GET | Allowed | Allowed | Allowed | Denied (401) |
| | `/auth/context-switch` | POST | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/auth/dev-login` | POST | Allowed | Allowed | Allowed | Allowed (Dev) |
| **Admin Operations** | `/admin/stats` | GET | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/health` | GET | Allowed | Allowed | Allowed | Allowed |
| | `/admin/documents/upload` | POST | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/documents/{id}/review` | PUT | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/results/import` | POST | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/results/all` | GET | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/audit-logs` | GET | Allowed | Denied (403) | Denied (403) | Denied (401) |
| **Roster & Excel** | `/admin/roster/preview` | POST | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/roster/import` | POST | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/roster/export/{type}` | GET | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/roster/sync-status` | GET | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/roster/users/{id}/institutional-fields` | PUT | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/admin/roster/users/{id}/status` | POST | Allowed | Denied (403) | Denied (403) | Denied (401) |
| **Website & Portals** | `/website/sources` | GET | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/website/crawl` | POST | Allowed | Denied (403) | Denied (403) | Denied (401) |
| | `/website/portals` | GET | Allowed | Allowed | Allowed | Denied (401) |
| | `/website/stats` | GET | Allowed | Denied (403) | Denied (403) | Denied (401) |
| **Student Profiles** | `/students/me` | GET | Allowed (Context) | Denied (403) | Allowed | Denied (401) |
| | `/students/me` | PUT | Allowed (Context) | Denied (403) | Allowed (Editable) | Denied (401) |
| | `/students/discovery` | GET | Allowed | Allowed | Allowed | Denied (401) |
| **Faculty Profiles** | `/faculty/me` | GET | Allowed (Context) | Allowed | Denied (403) | Denied (401) |
| | `/faculty/me` | PUT | Allowed (Context) | Allowed (Editable) | Denied (403) | Denied (401) |
| | `/faculty/directory` | GET | Allowed | Allowed | Allowed | Denied (401) |
| **Academic Records** | `/academic/timetables` | GET | Allowed | Allowed | Allowed | Denied (401) |
| | `/academic/datesheets` | GET | Allowed | Allowed | Allowed | Denied (401) |
| | `/academic/calendars` | GET | Allowed | Allowed | Allowed | Denied (401) |
| | `/academic/results/my` | GET | Denied (Self-Only) | Denied | Allowed (Own Roll No) | Denied (401) |
| **AI Intelligence** | `/rag/assistant/query` | POST | Allowed (Unfiltered) | Allowed (Audience Filtered) | Allowed (Audience Filtered) | Denied (401) |
| | `/application-agent/chat` | POST | Allowed | Denied (403) | Allowed | Denied (401) |
| | `/applications/{id}/decide`| POST | Allowed | Allowed (Assigned Only) | Denied (403) | Denied (401) |

---

## 3. Field-Level Permission Matrix

### Student Profile Fields
| Field Name | Storage Location | Read Permission | Student Self-Edit | Super Admin Edit | Sync to Excel |
|---|---|---|:---:|:---:|:---:|
| `roll_number` | `users.roll_number` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `enrolment_number` | `student_profiles.enrolment_number` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `department` | `users.department_name` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `programme` | `student_profiles.programme` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `branch` | `users.branch` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `specialization` | `student_profiles.specialization` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `batch` | `student_profiles.batch` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `semester` | `student_profiles.semester` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `section` | `student_profiles.section` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `academic_year` | `student_profiles.academic_year` | Public/Student/Staff | **LOCKED (No)** | **Yes** | Yes |
| `date_of_admission`| `student_profiles.date_of_admission`| Student/Admin | **LOCKED (No)** | **Yes** | Yes |
| `bio` | `student_profiles.bio` | Public | **Yes** | Yes | Yes |
| `skills` | `student_skills` | Public | **Yes** | Yes | Yes |
| `projects` | `projects` | Public | **Yes** | Yes | Yes |
| `achievements` | `student_profiles.achievements` | Public | **Yes** | Yes | Yes |
| `certifications`| `student_profiles.certifications` | Public | **Yes** | Yes | Yes |
| `experience` | `student_profiles.experience` | Public | **Yes** | Yes | Yes |
| `resume_url` | `student_profiles.resume_url` | Mentors/Staff | **Yes** | Yes | Yes |
| `github_url` | `student_profiles.github_url` | Public | **Yes** | Yes | Yes |
| `linkedin_url` | `student_profiles.linkedin_url` | Public | **Yes** | Yes | Yes |
| `portfolio_url`| `student_profiles.portfolio_url` | Public | **Yes** | Yes | Yes |

### Faculty Profile Fields
| Field Name | Storage Location | Read Permission | Faculty Self-Edit | Super Admin Edit | Sync to Excel |
|---|---|---|:---:|:---:|:---:|
| `faculty_identifier`| `faculty_profiles.faculty_identifier` | Public | **LOCKED (No)** | **Yes** | Yes |
| `designation` | `faculty_profiles.designation` | Public | **LOCKED (No)** | **Yes** | Yes |
| `department` | `faculty_profiles.department` | Public | **LOCKED (No)** | **Yes** | Yes |
| `centre` | `faculty_profiles.centre` | Public | **LOCKED (No)** | **Yes** | Yes |
| `qualification`| `faculty_profiles.qualification` | Public | **LOCKED (No)** | **Yes** | Yes |
| `official_profile_url`| `faculty_profiles.official_profile_url` | Public | **LOCKED (No)** | **Yes** | Yes |
| `bio` | `faculty_profiles.bio` | Public | **Yes** | Yes | Yes |
| `office_location` | `faculty_profiles.office_location` | Public | **Yes** | Yes | Yes |
| `office_hours` | `faculty_profiles.office_hours` | Public | **Yes** | Yes | Yes |
| `email_public` | `faculty_profiles.email_public` | Public | **Yes** | Yes | Yes |
| `phone_public` | `faculty_profiles.phone_public` | Public | **Yes** | Yes | Yes |
| `research_areas` | `faculty_research_interests` | Public | **Yes** | Yes | Yes |
| `areas_of_expertise`| `faculty_profiles.areas_of_expertise` | Public | **Yes** | Yes | Yes |
| `publications` | `faculty_profiles.publications_json` | Public | **Yes** | Yes | Yes |

---

## 4. Audit Trail Enforcement
All actions performed by Super Admins (document publishing, marks imports, roster imports, context switches, institutional field alterations) write directly to the `audit_logs` table with:
- `actor_user_id` and `actor_email`
- `actor_role`
- `action` (e.g. `CONTEXT_SWITCH`, `ROSTER_IMPORT`, `UPDATE_INSTITUTIONAL_FIELDS`)
- `target_entity` and `target_id`
- `change_summary`
- `ip_address` and `user_agent`
- `created_at` (UTC timestamp)
- `extra_context` JSON metadata
