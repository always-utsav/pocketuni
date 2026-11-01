# PocketUni — Document Extraction & Academic Ingestion Architecture

## 1. Supported Document Categories (16 Standardized Types)

PocketUni defines 16 institutional document categories matching university operations:

| Category Code | Display Name | Target Audiences | Confidentiality Level |
|---|---|---|---|
| `ACADEMIC_CALENDAR` | Academic Calendar | All Students, Faculty | Public Institutional |
| `TIMETABLE` | Timetable / Class Schedule | Specific Year/Semester, Faculty | Departmental / Academic |
| `SYLLABUS` | Course Syllabus | Enrolled Students, Faculty | Academic Public |
| `SCHEME_OF_STUDY` | Scheme of Study / Credit Structure | Programme & Batch | Academic Public |
| `EXAM_SCHEDULE` | Examination Datesheet | Exam Enrolled Students | Academic Public |
| `HOLIDAY_LIST` | Holiday List | Campus-wide | Public Institutional |
| `FACULTY_DIRECTORY` | Faculty Directory | Campus-wide | Public Institutional |
| `FEES_CIRCULAR` | Fee Circular & Dues Schedule | Students, Accounts | Restricted Institutional |
| `SCHOLARSHIP_NOTICE` | Scholarship & Financial Aid | Eligible Students | Institutional Notice |
| `HOSTEL_NOTICE` | Hostel & Residential Rules | Hostel Residents | Residential |
| `PLACEMENT_CIRCULAR` | Placement & Training Circular | Final / Pre-final Years | Career Cell |
| `EVENT_NOTIFICATION` | Campus Event Notice | Campus-wide | General Campus |
| `STUDENT_HANDBOOK` | Student Handbook & Code of Conduct| All Students | Institutional Policy |
| `ADMISSION_POLICY` | Admission Rules & Ordinances | Prospective / New Students | Statutory |
| `INTERNAL_MARKS` | Internal Marks & Minor Assessment | Super Admin Only | **Confidential Institutional** |
| `GENERAL_NOTICE` | General Administrative Notice | Specified Target | General Notice |

## 2. Ingestion Pipeline for the 9 MITS CAI Documents

The system processes 9 reference documents uploaded from the MITS Centre for Artificial Intelligence:

1. **`Firsty_year_Induction_2025  .docx.pdf` (6 pages)**
   - *Extractor:* Native PyMuPDF text stream extractor.
   - *Classification:* `GENERAL_NOTICE` / Induction Programme.
   - *Extracted Data:* Event schedules, venue details, speaker sessions, reporting dates for incoming 2025-26 cohort.

2. **`II Year Scheme admitted in session 2025-26.pdf` (4 pages)**
   - *Extractor:* `pdfplumber` + PyMuPDF tabular parser.
   - *Classification:* `SCHEME_OF_STUDY`.
   - *Extracted Data:* Semester III & IV course codes (e.g., 250311, 250312), credit allocations, lecture-tutorial-practical (L-T-P) distribution, and evaluation scheme tables.

3. **`II Year Syllabus admitted in session 2025-26.pdf` (15 pages)**
   - *Extractor:* PyMuPDF structural parser.
   - *Classification:* `SYLLABUS` (2nd Year).
   - *Extracted Data:* Unit-by-unit syllabus breakdowns, course learning objectives, textbooks, reference materials, and lab assignments for B.Tech AI & Data Science.

4. **`III Year Syllabus session 2024-25.pdf` (29 pages)**
   - *Extractor:* PyMuPDF structural parser.
   - *Classification:* `SYLLABUS` (3rd Year).
   - *Extracted Data:* 5th and 6th semester specialized AI electives, prerequisites, course outcomes, and evaluation criteria.

5. **`III Sem TT July-Dec 2026.pdf` (4 pages - Scanned Image Timetable)**
   - *Extractor:* PyMuPDF page rendering (300 DPI) + Tesseract OCR engine (v5.5.0).
   - *Classification:* `TIMETABLE` (Semester III).
   - *Extracted Data:* Daily slot allocations (Period 1 to Period 7), lab batch allocations, room numbers, and faculty codes (e.g., MC for Dr. Mausam Chouksey).

6. **`V Sem TT July-Dec 2026.pdf` (4 pages - Scanned Image Timetable)**
   - *Extractor:* PyMuPDF + Tesseract OCR.
   - *Classification:* `TIMETABLE` (Semester V).
   - *Extracted Data:* 5th semester class timetable grid, lab sessions, and faculty designations.

7. **`VII Sem TT July-Dec 2026.pdf` (4 pages - Scanned Image Timetable)**
   - *Extractor:* PyMuPDF + Tesseract OCR.
   - *Classification:* `TIMETABLE` (Semester VII).
   - *Extracted Data:* 7th semester major project slots, elective lecture blocks, and mentoring periods.

8. **`Professional_Certification_Course_List.pdf` (3 pages)**
   - *Extractor:* PyMuPDF table extractor.
   - *Classification:* `GENERAL_NOTICE` / Professional Certification Course List.
   - *Extracted Data:* Approved NPTEL/Coursera/Swayam certification tracks, credit equivalencies, and minimum pass criteria.

9. **`2nd semester minor 2 Lab and theory marks.pdf` (12 pages - Confidential Student Records)**
   - *Extractor:* PyMuPDF grid parser + tabula-style regex extractor.
   - *Classification:* `INTERNAL_MARKS`.
   - *Privacy Protection:* Marked as strictly **Super Admin Only**. Never published to general campus audiences.
   - *Extracted Data:* Student enrollment numbers (e.g., BTAD24O101), lab marks, minor assessment scores, and attendance reconciliation summaries.

## 3. Tesseract OCR Configuration on Windows
- Binary Path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- Environment Variable: `TESSERACT_CMD` in `.env`
- Integration: Configured in `backend/app/services/extraction_service.py` with automatic fallback to native text parser if the document already contains selectable text (> 100 characters per page).
