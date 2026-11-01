# MITS Web Ecosystem & E-Governance Ingestion Report
## PocketUni — MITS Gwalior AI Platform

This report catalogues the digital web ecosystem of Madhav Institute of Technology & Science (MITS), Gwalior, and details how PocketUni integrates official institutional portals into the student and faculty workflow.

---

## 1. Official MITS Digital Infrastructure

MITS Gwalior operates several specialized web platforms for administration, academics, exams, and alumni affairs. PocketUni categorizes these systems into:
1. **Public Information Platforms:** Ingested into the AI knowledge base.
2. **Authenticated E-Governance Portals:** Catalogued with direct SSO / navigation links and service descriptions, with zero unauthorized data scraping.

---

## 2. Institutional E-Governance Directory Catalogue

The following systems are officially catalogued in the PostgreSQL `institutional_portals` table:

| Portal Code | Name | URL | Category | Target Audience | Auth Required | Purpose / Services Provided |
|---|---|---|:---:|:---:|:---:|---|
| **AMS** | Academic Management System | `https://ams.mitsgwalior.in/` | `ACADEMIC` | Students, Faculty | Yes | Attendance tracking, internal marks entry, course registration, semester fees payment. |
| **MIS** | Management Information System | `https://web.mitsgwalior.in/e-governance` | `ADMINISTRATIVE` | Faculty, Staff | Yes | Institutional payroll, leave management, HR administration, departmental assets. |
| **IMS** | Infrastructure Management System | `https://ims.mitsgwalior.in/` | `INFRASTRUCTURE` | Campus Community | Yes | Campus maintenance requests, IT support tickets, classroom AV issue resolution. |
| **MOODLE** | Moodle LMS Portal | `http://moodle.mitsgwalior.in/` | `ACADEMIC` | Students, Faculty | Yes | Online assignment submissions, lecture materials, course quizzes, discussion forums. |
| **ALUMNI** | MITS Alumni Association Portal | `https://alumni.mitsgwalior.in/` | `COMMUNITY` | Alumni, Students | Yes | Mentorship connections, alumni directories, reunion registrations, placement networking. |
| **NEC** | National Employment Consortium | `https://nec.mitsgwalior.in/` | `CAREERS` | Students, T&P Cell | Yes | Placement drives coordination, recruiter test links, interview scheduling. |
| **OSM** | On-Screen Marking System | `https://osm.mitsgwalior.in/` | `EXAMINATION` | Evaluators, COE | Yes | High-security digital answer script evaluation for university examinations. |
| **RRS** | Result Retrieval System | `https://results.mitsgwalior.in/` | `EXAMINATION` | Students | Yes | Official semester grade cards, back-paper results, revaluation status. |

---

## 3. Security, Privacy & SSRF Defenses

1. **Strict SSRF Firewall:** The crawler enforces an institutional domain allowlist:
   - `web.mitsgwalior.in`
   - `ams.mitsgwalior.in`
   - `mitsgwalior.in`
   Requests attempting to resolve internal addresses (`127.0.0.1`, `localhost`, `0.0.0.0`, `169.254.169.254`, private class A/B/C subnets) are dropped immediately.
2. **Privacy Boundary:** The crawler **never** attempts to scrape authenticated student portals, examination databases, or personal salary information.
3. **Robots Polite Polling:** Requests are throttled with a mandatory 0.5-second delay between pages to prevent server load spikes on institutional infrastructure.
