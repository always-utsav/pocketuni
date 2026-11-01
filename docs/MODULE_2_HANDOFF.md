# PocketUni Module 2: Architectural Handoff & Prerequisites

**Handoff From**: Module 1 (Foundation, Authentication, Database, Super Admin & Document Management)  
**Target Module**: Module 2 (AI, Gemini Integration, Embeddings & Grounded RAG Pipeline)  
**Status**: Ready for Module 2 Kickoff

---

## 1. Module Boundary & State of the Codebase

Module 1 has established all prerequisites for advanced AI capabilities without prematurely implementing or mocking Module 2 components:

1. **Relational Foundation**: All extracted text chunks, structured tables, and metadata from institutional documents are persisted in `extracted_document_contents` and `extracted_tables`.
2. **Audience Filtering**: The backend already filters documents by student and faculty audience (`backend/app/services/audience_service.py`), ready to serve as the pre-retrieval filter in the RAG pipeline.
3. **Conversational Models**: `conversations`, `messages`, and `feedbacks` tables are defined and ready for RAG query history persistence.
4. **Clean Frontend Hooks**: `ChatView.tsx` and `ragEngine.ts` remain active and cleanly isolated, ready to be wired to the streaming RAG endpoint in Module 2.

---

## 2. Prerequisites for Module 2

Prior to commencing Module 2 execution, ensure the following keys and configurations are provisioned:

1. **Gemini API Key**: Set `GEMINI_API_KEY` in `.env` (configured via Google AI Studio).
2. **Vector Extension (`pgvector`)**:
   - For PostgreSQL 18 on Windows, ensure the `pgvector` extension library is present if vector cosine similarity is computed directly in-database.
   - Alternatively, a lightweight local embedding index (e.g. ChromaDB or in-process FAISS) can be utilized if local `pgvector` binaries require compilation.
3. **Database Connection String**:
   - Ensure `POSTGRES_PASSWORD` is configured in `.env` for production database operations on `localhost:5432/pocketuni`.

---

## 3. Module 2 Scope & Interfaces to Implement

| Component | Responsibility | Interface / Target Path |
|---|---|---|
| **Vector Embedding Service** | Chunk extracted documents (semantic text splitter) and compute dense embeddings using `text-embedding-004`. | `backend/app/services/embedding_service.py` |
| **Hybrid Retrieval Engine** | Combine BM25 keyword matching with vector semantic search, applying audience metadata filters. | `backend/app/services/retrieval_service.py` |
| **Grounded Gemini Assistant** | Stream answers character-by-character using Gemini 1.5 Pro / Flash with strict citation chips (`[1]`, `[2]`). | `backend/app/api/v1/routes/chat.py` |
| **Slot-Filling Application Agent** | Connect the multi-step finite state machine with conversational intent parsing. | `backend/app/services/agent_service.py` |
| **Discovery Search Engine** | Semantic and skill-based matching for student project discovery and faculty research queries. | `backend/app/services/discovery_service.py` |

---

## 4. Integrity Checklist Before Module 2

- [x] All 50 SQLAlchemy models mapped and migrated via Alembic.
- [x] Super Admin server-side allowlist active and tested.
- [x] Multi-format document parser handles PDF, DOCX, XLSX, and OCR.
- [x] 12/12 automated backend unit and integration tests passing.
- [x] Frontend builds with 0 TypeScript errors under refined visual tokens.
- [x] Mentor profile for Dr. Mausam Chouksey verified and accessible.
