# PocketUni — Institutional RAG Pipeline & Vector Retrieval

## 1. Overview
The PocketUni Retrieval-Augmented Generation (RAG) pipeline grounds AI responses in verified academic documents from MITS Gwalior (focusing on the Centre for Artificial Intelligence).

```
   User Query
       │
       ▼
1. User Scope Resolution (Role, Branch, Semester from PostgreSQL)
       │
       ▼
2. SQL Pre-Filter (Excludes Drafts, Superseded, Internal Marks)
       │
       ▼
3. Gemini Embedding (gemini-embedding-001 -> 3072 floats)
       │
       ▼
4. Hybrid Scoring (Dense Cosine Sim 75% + Lexical Overlap 25%)
       │
       ▼
5. Context Assembly with Source Citations [Doc Title, Page X]
       │
       ▼
6. Grounded Synthesis via Gemini (gemini-2.5-flash)
       │
       ▼
Answer with Real Citations
```

## 2. Ingested & Indexed Documents in PostgreSQL

| Document | Category | Total Chunks | Indexed Model | Status |
|---|---|---|---|---|
| `Firsty_year_Induction_2025  .docx.pdf` | `INDUCTION_NOTICE` | 25 | `gemini-embedding-001` | **INDEXED** |
| `II Year Scheme admitted in session 2025-26.pdf` | `SCHEME_OF_STUDY` | 48 | `gemini-embedding-001` | **INDEXED** |
| `II Year Syllabus admitted in session 2025-26.pdf` | `SYLLABUS` | 97 | `gemini-embedding-001` | **INDEXED** |
| `III Sem TT July-Dec 2026.pdf` | `TIMETABLE` (OCR) | 5 | `gemini-embedding-001` | **INDEXED** |
| `III Year Syllabus session 2024-25.pdf` | `SYLLABUS` | 201 | `gemini-embedding-001` | **INDEXED** |
| `Professional_Certification_Course_List.pdf` | `PROFESSIONAL_CERTIFICATION_LIST`| 16 | `gemini-embedding-001` | **INDEXED** |
| `V Sem TT July-Dec 2026.pdf` | `TIMETABLE` (OCR) | 5 | `gemini-embedding-001` | **INDEXED** |
| `VII Sem TT July-Dec 2026.pdf` | `TIMETABLE` (OCR) | 5 | `gemini-embedding-001` | **INDEXED** |
| `2nd semester minor 2 Lab and theory marks.pdf` | `INTERNAL_MARKS` | **0** | None (Confidential) | **EXCLUDED** |

**Total Chunks in PostgreSQL:** 402 chunks  

## 3. Grounding & Anti-Injection Rules
1. **Evidence as Untrusted Content:** Chunks are fed into the prompt between strict boundary delimiters. The system prompt directs the model to treat chunk text solely as evidence and never as executive commands.
2. **Page-Level Citations:** Citations include the official document title and exact source page number (e.g. `[II Year Scheme admitted in session 2025-26, Page 2]`).
3. **Abstention Policy:** If the retrieved evidence does not contain verified factual answers, the assistant explicitly replies that verified institutional documentation is not available.
