# Knowledge Ingestion & Document Processing Pipeline

## 1. Overview
The PocketUni Knowledge Ingestion Pipeline transforms official institutional documents from the MITS Centre for Artificial Intelligence into grounded, searchable representations within PostgreSQL 18.

The pipeline ensures:
1. **Accurate Document Representation**: Clean extraction of multi-column syllabuses, credit schemes, induction notifications, and timetables.
2. **OCR Integration**: Robust optical character recognition via Tesseract 5.5 for scanned and rasterized timetable matrices.
3. **Structure-Aware Chunking**: Specialized strategies per document type preserving semantic cohesion, table headers, and hierarchical relationships.
4. **Vector Embedding**: Generating 3072-dimensional embeddings via Google Gemini (`gemini-embedding-001`).
5. **Strict Data Segregation**: Confidential internal marks documents (`INTERNAL_MARKS`) are completely excluded from RAG chunking and vector indexing.

---

## 2. Ingested Documents Inventory

| Document Name | Extracted Type | Page Count | Chunks Generated | Indexing Status | Sensitivity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Firsty year Induction 2025  .docx.pdf` | NOTICE / CIRCULAR | 7 | 25 | `INDEXED` | Public / Students |
| `II Year Scheme admitted in session 2025-26.pdf` | SCHEME | 4 | 48 | `INDEXED` | Academic Public |
| `II Year Syllabus admitted in session 2025-26.pdf` | SYLLABUS | 19 | 97 | `INDEXED` | Academic Public |
| `III Sem TT July-Dec 2026.pdf` | TIMETABLE (OCR) | 1 | 5 | `INDEXED` | Batch Specific |
| `III Year Syllabus session 2024-25.pdf` | SYLLABUS | 40 | 201 | `INDEXED` | Academic Public |
| `Professional Certification Course List.pdf` | NOTICE / CIRCULAR | 4 | 16 | `INDEXED` | Academic Public |
| `V Sem TT July-Dec 2026.pdf` | TIMETABLE (OCR) | 1 | 5 | `INDEXED` | Batch Specific |
| `VII Sem TT July-Dec 2026.pdf` | TIMETABLE (OCR) | 1 | 5 | `INDEXED` | Batch Specific |
| `2nd semester minor 2 Lab and theory marks.pdf` | INTERNAL_MARKS | 1 | 0 | `RESTRICTED` | Confidential |

**Total Vector Chunks in PostgreSQL:** 402 chunks across 8 public documents.

---

## 3. Structure-Aware Chunking Strategies

Implemented in `backend/app/services/chunking_service.py`:

### A. Syllabus Chunking (`chunk_syllabus`)
- **Hierarchy Detection**: Detects course headers (e.g., `Course Code: 24252101`, `Subject Name: Machine Learning`).
- **Module Preservation**: Segregates content into Course Overview, Prerequisites, Units/Modules (Unit 1 through Unit 5), Course Outcomes (COs), and Recommended Textbooks.
- **Context Preservation**: Prepends subject title and course code to every individual unit chunk to guarantee dense retrieval accuracy when students ask unit-specific questions.

### B. Scheme Chunking (`chunk_scheme`)
- **Tabular Row Parsing**: Preserves credit distributions (L-T-P), Total Credits, Contact Hours, End-Semester exam weightage, and Mid-Semester continuous evaluation components.
- **Semester Partitioning**: Ensures each semester scheme is indexed with full column context so queries like *"How many credits in semester IV?"* retrieve exact numerical credits without hallucinations.

### C. Timetable Matrix Chunking (`chunk_timetable`)
- **Tesseract OCR Extraction**: Runs Tesseract OCR with PSM 6 (uniform block of text) and custom contrast enhancement for scanned PNG/PDF page images.
- **Day/Slot Alignment**: Normalizes schedule rows by Day (Monday through Saturday) and Time Slot (10:00 AM - 5:00 PM).
- **Faculty & Room Annotations**: Embeds room numbers and faculty initials alongside subject codes to allow schedule querying by subject, day, or instructor.

### D. Notice & Calendar Chunking (`chunk_notice_or_calendar`)
- **Event-Driven Paragraph Slicing**: Splits on numbered items, bullet points, dates, and deadlines.
- **Target Audience Metadata**: Attaches metadata indicating applicable batches (e.g., "First Year Admitted 2025-26") to avoid cross-batch confusion.

---

## 4. Confidential Marks Isolation

### Rule & Verification:
- Documents identified with category `INTERNAL_MARKS` or containing student scores/grades are strictly prohibited from entering `document_chunks`.
- In `backend/app/ingest_real_docs.py` and `backend/app/services/chunking_service.py`:
  ```python
  if doc.doc_type == DocumentType.INTERNAL_MARKS:
      logger.info(f"Skipping RAG indexing for confidential marks document: {doc.title}")
      doc.indexing_status = "RESTRICTED"
      db.commit()
      return []
  ```
- Result: `2nd semester minor 2 Lab and theory marks.pdf` has **0 vector chunks** in `document_chunks`, ensuring zero leakage of student marks through general AI chat queries. Individual grade lookups are delegated to verified authenticated student profile APIs.

---

## 5. Ingestion Workflow & Execution

To re-run or update institutional ingestion:
```powershell
& .\backend\.venv\Scripts\python.exe -m backend.app.ingest_real_docs
```

The script:
1. Connects to PostgreSQL 18.
2. Reads files from `.user_uploaded/` or repository root.
3. Performs layout-aware text extraction (PDFPlumber / PyPDF2 / Tesseract).
4. Slices text using `chunking_service.py`.
5. Batches chunks and calls `GeminiService.embed_texts()` using `gemini-embedding-001`.
6. Upserts chunks into `document_chunks` table with JSON vector representations.
7. Updates document status to `INDEXED` with `indexed_chunks_count`.
