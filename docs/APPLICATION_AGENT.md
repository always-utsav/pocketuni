# Conversational Application Agent & Workflow Automation

## 1. Overview
The Conversational Application Agent empowers MITS students to draft formal academic applications (e.g., Leave of Absence, Bonafide Certificate, Fee Concession, Lab Access Request, NOC for Internship) through natural dialogue in `ApplicationAgentChat`.

The agent guides students through structured slot-filling, prefills verified profile attributes from PostgreSQL, allows real-time edits, generates formal `.docx` files via `python-docx`, submits them to the faculty inbox, and tracks decisions.

---

## 2. Slot-Filling Architecture

Implemented in `backend/app/services/application_agent_service.py`:

The agent maintains a state machine tracking required and optional fields:

| Application Type | Required Slots | Prefilled From DB | Student Must Provide |
| :--- | :--- | :--- | :--- |
| **Leave of Absence** | Start Date, End Date, Reason, Medical Certificate (if $>3$ days) | Name, Roll Number, Branch, Year | Dates, Medical reason |
| **Bonafide Certificate** | Purpose of Certificate, Academic Year | Name, Roll Number, Branch, Current Sem | Purpose (e.g., Passport, Bank Loan) |
| **Internship NOC** | Organization Name, Role, Duration, Start Date, Offer Letter | Name, Roll Number, CGPA, Branch | Company, Dates, Role |
| **Lab Access Request** | Lab Name, Purpose, Faculty Supervisor, Required Time Slots | Name, Roll Number, Department | Lab, Research Topic, Guide |

### Workflow Stages:
```
[User initiates chat] ──> [Detect Intent & Application Type]
                             │
                             ▼
                    [Prefill Verified DB Info]
                             │
                             ▼
                    [Query Missing Slots Iteratively]
                             │
                             ▼
                    [Present Preview & Allow Edits]
                             │
                             ▼
                    [Generate .docx & Submit to DB]
                             │
                             ▼
                    [Faculty Inbox: Share/Approve/Reject]
```

---

## 3. Formal Document Generation (`python-docx`)

Once all slots are validated, the system compiles a standardized letterhead document:
1. **MITS Header**:
   - Madhav Institute of Technology & Science, Gwalior (M.P.)
   - Centre for Artificial Intelligence
2. **Student Details**:
   - Student Name, Enrollment / Roll No., Department, Semester
3. **Formal Subject Line**:
   - `Subject: Application for [Application Type] - [Roll Number]`
4. **Body Text**:
   - Professionally formatted paragraphs containing filled slot details.
5. **Sign-off Block**:
   - Student signature placeholder, submission timestamp, and faculty recommendation section.

Students and faculty can download this document directly via `GET /api/v1/applications/{id}/docx`.

---

## 4. Faculty Review & Audit Workflow

1. **Inbox Integration**: Faculty see all pending student requests in `ApplicationListView` and inspect details in `ApplicationDetailView`.
2. **Review Actions**:
   - `APPROVED`: Records decision, timestamp, and optional faculty remarks.
   - `REJECTED`: Requires mandatory reason for rejection so the student can rectify deficiencies.
   - `SHARED`: Applications can be routed or forwarded to department HODs or coordinators.
3. **Audit Trail**: Every status transition generates an entry in `application_timeline` with the actor's ID and timestamp.
