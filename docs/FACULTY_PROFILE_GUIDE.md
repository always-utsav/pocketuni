# Faculty Profile & Mentorship Management Guide
## PocketUni — MITS Gwalior AI Platform

This guide outlines the faculty profile system, official institutional verification badges, locked academic records, and mentorship workflows.

---

## 1. Locked Institutional Faculty Credentials

Faculty members represent official academic authorities at MITS Gwalior. Institutional credentials extracted from the official MITS Web portal (`web.mitsgwalior.in`) or entered via administrative roster imports are protected from unauthorized modification.

### Verified Official Source Card
In `FacultyProfileView`, these verified credentials appear with a padlock indicator and a `Verified Official Source` badge:

- **Faculty Identifier:** Institutional employee code (e.g. `FAC-CAI-001`).
- **Official Designation:** Current appointment (e.g. `Professor & Head`, `Associate Professor`).
- **Department & Centre:** Official departmental affiliation (e.g. `Centre for Artificial Intelligence`).
- **Official Qualifications:** Terminal degrees (e.g. `Ph.D. (Computer Science), M.Tech`).
- **MITS Web Portal URL:** Direct link to the professor's live profile on `web.mitsgwalior.in`.

These attributes can only be modified by a Super Administrator via Tab 16 of the Super Admin Portal.

---

## 2. Faculty Self-Service Management

Faculty members have full autonomy to manage their academic availability, consultation schedules, and research information via `PUT /api/v1/faculty/me`:

- **Biography & Research Statement:** Academic background, research focus, current lab projects.
- **Office Hours & Consultation:** Exact days, times, and location for student consultations (e.g. `Monday & Wednesday, 2:00 PM – 4:00 PM`).
- **Physical Office Location:** Cabin / lab number (e.g. `Room 204, Centre for AI Building`).
- **Contact Visibility Controls:** Dedicated toggles for `emailPublic` and `phonePublic` to guard personal contact privacy while remaining reachable.
- **Research Interests & Domain Expertise:** Keywords indexed into the student discovery engine for mentor matching (e.g. `Medical Imaging`, `Computer Vision`, `LLM Grounding`).
- **Publications & Funded Projects:** Structured lists of recent journal articles, conference papers, and sponsored research projects.

---

## 3. Mentorship & Application Workflows

1. **Student Application Routing:** Students generate formal letters (NOC, Leave, Bonafide) using the conversational Application Agent and submit them to their assigned faculty mentor.
2. **Faculty Review Pane:** Faculty members log in with their `@mitsgwalior.in` Google account and access their pending applications dashboard.
3. **Decisions & Remarks:** Faculty can approve or reject applications with attached official remarks and signature metadata.
4. **Audit & Synchronization:** All profile modifications trigger an event in `audit_logs` and update `pocketuni_faculty.xlsx` in real time.
