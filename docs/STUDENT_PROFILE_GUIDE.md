# Student Profile System & Field Ownership Guide
## PocketUni — MITS Gwalior AI Platform

This document describes the student profile architecture, separating locked institutional credentials from user-editable career fields.

---

## 1. Locked Institutional Profile Credentials

To ensure academic authenticity and prevent transcript falsification, institutional fields are **strictly read-only** for students. These fields are verified by the college registrar and can only be altered by a Super Administrator.

### Verified Institutional Card
On the student profile screen (`StudentProfileView`), these fields are displayed in a highlighted institutional banner with a padlock icon and a `Verified by Registrar` badge:

- **Roll Number:** Fixed institutional identifier (e.g. `0901CS231001` or `DEMO-0901AI231001`).
- **Enrolment Number:** Permanent university registration identifier.
- **Academic Programme:** Degree level (e.g. `B.Tech`, `M.Tech`).
- **Department:** Academic division (e.g. `Centre for Artificial Intelligence`).
- **Branch / Specialization:** Specific branch and track (e.g. `AIML` / `Deep Learning`).
- **Batch:** Admitted cohort span (e.g. `2023-2027`).
- **Current Semester:** Current academic semester (e.g. `Semester 5`).
- **Section:** Grouping letter (e.g. `Section A`).
- **Academic Year:** Current session (e.g. `2026-2027`).

### Security Enforcement
When a student submits an update via `PUT /api/v1/students/me`, the backend ignores any incoming values for `rollNumber`, `enrolmentNumber`, `programme`, `branch`, `batch`, `semester`, or `section`. Even if a malicious request attempts to inject altered values, the database columns remain completely untouched.

---

## 2. Student Self-Service Editable Fields

Students have complete control over their professional and career presence on PocketUni. These fields feed into the **Peer Discovery Engine** and **Hackathon Matching**:

- **Biography & Objective:** About summary, statement of purpose, research interests.
- **Skills Portfolio:** Categorized technical proficiencies (Python, PyTorch, ROS, React, Docker).
- **Projects Showcase:** Title, description, GitHub repository link, live demo URL, tech stack tags.
- **Achievements & Certifications:** Hackathon wins, research grants, cloud/AI certifications.
- **Internships & Experience:** Professional roles, organization, duration, responsibilities.
- **Social & Professional Links:** GitHub, LinkedIn, personal portfolio, blog.
- **Resume URL:** Link to current verified curriculum vitae.
- **Availability & Collaboration:** `openForHackathons`, `lookingFor` collaborator notes, preferred roles (e.g. `ML Engineer`, `Frontend Dev`).

---

## 3. Background Sync & Audit Logging

Whenever a student saves changes to their editable profile:
1. An immutable audit event is logged in `audit_logs` (`action="STUDENT_PROFILE_UPDATE"`).
2. The `excel_service.sync_user_profile(db, student_id)` pipeline is triggered.
3. The background sync updates the corresponding row in `pocketuni_students.xlsx` using atomic temporary file replacement, ensuring offline workbooks never fall out of date.
