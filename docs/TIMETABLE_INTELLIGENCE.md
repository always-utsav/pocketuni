# Timetable Intelligence & Scheduling Engine Architecture
**Madhav Institute of Technology & Science (MITS-DU), Gwalior**  
**Department:** Centre for Artificial Intelligence  
**Academic Session:** July–December 2026

---

## 1. System Overview

PocketUni features a dedicated, relational timetable engine rather than raw string searching. All timetable queries from students or faculty are resolved deterministically against structured database rows parsed from official institute time tables (`III Sem TT July-Dec 2026.pdf`, `V Sem TT July-Dec 2026.pdf`, `VII Sem TT July-Dec 2026.pdf`).

---

## 2. Relational Schema & Models

The PostgreSQL schema uses the `timetable_entries` table with the following core fields:

| Column | Type | Description |
|---|---|---|
| `id` | VARCHAR(36) | Primary Key UUID |
| `day` | VARCHAR(20) | Day of week (`Monday` to `Saturday`) |
| `start_time` | VARCHAR(20) | Period start time (e.g. `09:30 AM`) |
| `end_time` | VARCHAR(20) | Period end time (e.g. `10:30 AM`) |
| `slot_number` | INTEGER | Period index (1 to 6) |
| `subject` | VARCHAR(255) | Official course title |
| `subject_code` | VARCHAR(50) | Official course alphanumeric code |
| `faculty_name` | VARCHAR(255) | Full name of teaching faculty |
| `room` | VARCHAR(100) | Classroom or laboratory venue (e.g. `M201`, `SH1`) |
| `branch` | VARCHAR(100) | Full branch title |
| `semester` | VARCHAR(20) | Semester label (e.g. `III Semester`, `V Semester`) |
| `section` | VARCHAR(20) | Section identifier (`A`, `B`, `1`, `2`) |
| `is_lab` | INTEGER | Flag indicating laboratory session (1) or lecture (0) |
| `effective_period` | VARCHAR(100) | Academic semester validity (`July-Dec 2026`) |

---

## 3. Standard Period Timings (Centre for AI)

| Period | Start Time | End Time | Label |
|---|---|---|---|
| **Period 1** | 09:30 AM | 10:30 AM | Morning Slot 1 |
| **Period 2** | 10:30 AM | 11:30 AM | Morning Slot 2 |
| **Period 3** | 11:30 AM | 12:30 PM | Pre-Lunch Slot |
| **Lunch Break** | 12:30 PM | 01:30 PM | Department Lunch Break |
| **Period 4** | 01:30 PM | 02:30 PM | Afternoon Slot 1 |
| **Period 5** | 02:30 PM | 03:30 PM | Afternoon Slot 2 |
| **Period 6** | 03:30 PM | 04:30 PM | Evening / Lab Slot |

---

## 4. Authoritative Faculty Initials Mapping (Page 4 Master TT)

The timetable engine includes an exact reverse mapping of all faculty codes:

- `RRS` -> Dr. Rajni Ranjan Singh Makwana
- `AS` -> Dr. Anu Sayal
- `MSA` -> Dr. Mir Shahnawaz Ahmad
- `AK` -> Dr. Arun Kumar
- `TS` -> Dr. Tej Singh
- `VT` -> Dr. Vibha Tiwari
- `SKS` -> Dr. Sunil Kumar Shukla
- `SD` -> Dr. Sumit Dhariwal
- `SM` -> Dr. Shubha Mishra
- `SS` -> Dr. Shipra Shukla
- `SO` -> Dr. Satyam Omar
- `RKS` -> Dr. Rahul Kumar Sharma
- `PD` -> Dr. Pawan Dubey
- `NM` -> Dr. Neeraj Mishra
- `NA` -> Dr. Neelam Arya
- `MC` -> Dr. Mausam Chouksey
- `HSP` -> Dr. Hardev Singh Pal
- `BSR` -> Dr. Bhagat S. Raghuwanshi
- `AST` -> Dr. Anurag Singh Tomar
- `AB` -> Dr. Abhishek Bhatt
- `VSS` -> Dr. Vijay Shankar Sharma
- `RDP` -> Dr. Rishabh Deo Pandey
- `NH` -> Dr. Nidhi Humnekar
- `PSK` -> Dr. Pritha Singh Kushwah
- `MS` -> Dr. Mehuli Santra
- `PT` -> Ms. Pooja Tripathi
- `AA` -> Ms. Archana Acharya
- `GH` -> Mrs. Geetika Hazra
- `RS` -> Mr. Ramnaresh Sharma
- `RST` -> Mr. Rahul Senthiya

---

## 5. Personalized Student Schedule Resolution

When a student asks:
> *"What is my timetable tomorrow?"*

The system executes:
1. Identifies authenticated student's branch (`Information Technology (Artificial Intelligence and Robotics)`), semester (`III Semester`), and section (`A`).
2. Calculates tomorrow's day in `Asia/Kolkata` timezone (e.g. `Tuesday`).
3. Queries `timetable_entries` for matching slots ordered by `slot_number ASC`.
4. Returns clean, structured markdown table along with the `TIMETABLE_CARD` UI widget.
5. If the target day is `Sunday`, returns a clean holiday message (`is_holiday: true`).

---

## 6. Faculty Availability Resolver & Disclaimer

When an inquiry asks:
> *"Which teacher is free at 2 PM on Tuesday?"*

The engine:
1. Maps `2 PM` to Period 4 (`01:30 PM - 02:30 PM`).
2. Queries all faculty members actively assigned to a class in Period 4 on Tuesday.
3. Computes the complement set of CAI faculty members who have no classroom teaching.
4. Generates a list of free faculty members with designations and office rooms.
5. Injects the **Mandatory Non-Confirmation Disclaimer**:
   > *"Note: Faculty availability is derived from published master teaching timetables (Asia/Kolkata). Faculty without scheduled classes may still be engaged in departmental meetings, research, administrative duties, examination coordination, or student mentoring. Please verify urgent meetings directly via institutional email or during designated office hours."*
