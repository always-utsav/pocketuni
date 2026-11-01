import re
from typing import List, Dict, Any, Optional

class DocumentChunkDTO:
    def __init__(
        self,
        chunk_text: str,
        chunk_index: int,
        source_page_number: Optional[int] = None,
        source_section: Optional[str] = None,
        token_count: int = 0
    ):
        self.chunk_text = chunk_text
        self.chunk_index = chunk_index
        self.source_page_number = source_page_number
        self.source_section = source_section
        self.token_count = token_count or max(1, len(chunk_text.split()))


class ChunkingEngine:
    """
    Structure-aware chunking engine tailored for academic university documents.
    Preserves tables, timetable grids, units, and headers without blind fixed slicing.
    """

    def chunk_document(
        self,
        category: str,
        contents: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunkDTO]:
        # Guard: INTERNAL_MARKS must never enter general institutional chunking
        if category == "INTERNAL_MARKS":
            return []

        chunks: List[DocumentChunkDTO] = []
        chunk_idx = 0

        # Dispatch based on document structure
        if category == "TIMETABLE":
            chunks = self._chunk_timetable(contents, tables, metadata)
        elif category in ("SCHEME_OF_STUDY", "SYLLABUS"):
            chunks = self._chunk_scheme_or_syllabus(category, contents, tables, metadata)
        elif category == "ACADEMIC_CALENDAR":
            chunks = self._chunk_calendar(contents, tables, metadata)
        else:
            chunks = self._chunk_general(contents, tables, metadata)

        # Assign strictly sequential indices
        for i, c in enumerate(chunks):
            c.chunk_index = i

        return chunks

    def _chunk_timetable(
        self,
        contents: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> List[DocumentChunkDTO]:
        chunks = []
        sem = (metadata or {}).get("semester") or "Semester Schedule"
        prog = (metadata or {}).get("programme") or "B.Tech"
        branch = (metadata or {}).get("branch") or "Artificial Intelligence"

        # 1. Process structured tables
        for tbl in tables:
            headers = tbl.get("headers", [])
            rows = tbl.get("rows", [])
            page = tbl.get("page_number", 1)

            # Chunk by rows or day groupings
            current_day = ""
            for row_idx, row in enumerate(rows):
                row_str = " | ".join(str(c) for c in row if c)
                if not row_str.strip():
                    continue
                # Identify if day row
                first_cell = str(row[0]).strip().upper() if row else ""
                if first_cell in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]:
                    current_day = first_cell

                section_title = f"{sem} Timetable - {current_day or f'Row {row_idx+1}'}"
                text = (
                    f"MITS Gwalior {prog} {branch} {sem} Class Schedule.\n"
                    f"Day: {current_day or 'Scheduled Day'}\n"
                    f"Slot Details: {row_str}\n"
                    f"Columns: {' | '.join(str(h) for h in headers)}"
                )
                chunks.append(DocumentChunkDTO(
                    chunk_text=text,
                    chunk_index=len(chunks),
                    source_page_number=page,
                    source_section=section_title
                ))

        # 2. Process textual OCR/extracted content blocks (e.g. room allocations, teacher codes)
        for item in contents:
            text = item.get("content", "").strip()
            page = item.get("page_number", 1)
            if len(text) < 40:
                continue
            # If text contains faculty initials or room info, make dedicated chunks
            if any(k in text for k in ["Faculty Initial", "Class Room", "Lab No", "Dr.", "Prof."]) or len(text) > 200:
                chunks.append(DocumentChunkDTO(
                    chunk_text=f"MITS Timetable Notes & Room/Faculty Reference ({sem}, Page {page}):\n{text}",
                    chunk_index=len(chunks),
                    source_page_number=page,
                    source_section=f"Timetable Details Page {page}"
                ))

        return chunks

    def _chunk_scheme_or_syllabus(
        self,
        category: str,
        contents: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> List[DocumentChunkDTO]:
        chunks = []
        sem = (metadata or {}).get("semester") or ""
        batch = (metadata or {}).get("batch") or ""

        # 1. Tables in Schemes represent credit matrices, course codes, and contact hours
        for tbl in tables:
            headers = tbl.get("headers", [])
            rows = tbl.get("rows", [])
            page = tbl.get("page_number", 1)
            header_str = " | ".join(str(h) for h in headers)

            # Bundle related table rows (3-5 rows per chunk for cohesive course block)
            batch_size = 4
            for i in range(0, len(rows), batch_size):
                sub_rows = rows[i:i + batch_size]
                rows_text = "\n".join(" | ".join(str(c) for c in r if c) for r in sub_rows)
                text = (
                    f"MITS Scheme of Study & Examination Matrix ({sem} {batch}, Page {page}):\n"
                    f"Structure Headers: {header_str}\n"
                    f"Course Breakdown:\n{rows_text}"
                )
                chunks.append(DocumentChunkDTO(
                    chunk_text=text,
                    chunk_index=len(chunks),
                    source_page_number=page,
                    source_section=f"{sem} Course Credit Distribution"
                ))

        # 2. Paragraphs / Units in Syllabus
        current_unit = None
        buffer_text = []
        current_page = 1

        for item in contents:
            text = item.get("content", "").strip()
            page = item.get("page_number", 1)
            heading = item.get("heading") or ""

            # Check if text introduces a new Unit or Course
            if re.search(r'(Unit\s*[-–—:]*\s*[IVX0-9]+|Course Code|Course Title|Recommended Books)', text, re.I):
                if buffer_text:
                    full_chunk = "\n\n".join(buffer_text)
                    if len(full_chunk) > 50:
                        chunks.append(DocumentChunkDTO(
                            chunk_text=f"MITS Academic Syllabus ({sem}):\n{full_chunk}",
                            chunk_index=len(chunks),
                            source_page_number=current_page,
                            source_section=current_unit or "Syllabus Module"
                        ))
                    buffer_text = []
                current_unit = heading or text.split("\n")[0][:80]
                current_page = page

            buffer_text.append(text)

            # Flush when buffer reaches comfortable semantic size (~600-900 chars)
            if sum(len(t) for t in buffer_text) > 800:
                full_chunk = "\n\n".join(buffer_text)
                chunks.append(DocumentChunkDTO(
                    chunk_text=f"MITS Academic Syllabus ({sem}):\n{full_chunk}",
                    chunk_index=len(chunks),
                    source_page_number=current_page,
                    source_section=current_unit or "Syllabus Content"
                ))
                buffer_text = []

        if buffer_text:
            chunks.append(DocumentChunkDTO(
                chunk_text=f"MITS Academic Syllabus ({sem}):\n" + "\n\n".join(buffer_text),
                chunk_index=len(chunks),
                source_page_number=current_page,
                source_section=current_unit or "Syllabus Content"
            ))

        return chunks

    def _chunk_calendar(
        self,
        contents: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> List[DocumentChunkDTO]:
        chunks = []
        # Chunk calendar entries grouped by month or milestones
        for item in contents:
            text = item.get("content", "").strip()
            page = item.get("page_number", 1)
            if len(text) < 30:
                continue
            chunks.append(DocumentChunkDTO(
                chunk_text=f"MITS Official Academic Calendar Milestone:\n{text}",
                chunk_index=len(chunks),
                source_page_number=page,
                source_section="Academic Calendar Dates"
            ))
        return chunks

    def _chunk_general(
        self,
        contents: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> List[DocumentChunkDTO]:
        chunks = []
        # General notice or document: chunk by heading or section
        buffer = []
        current_page = 1
        current_heading = "General Notice"

        for item in contents:
            text = item.get("content", "").strip()
            page = item.get("page_number", 1)
            heading = item.get("heading")

            if heading:
                current_heading = heading

            if len(text) < 20:
                continue

            buffer.append(text)
            if sum(len(t) for t in buffer) > 700:
                chunks.append(DocumentChunkDTO(
                    chunk_text="\n\n".join(buffer),
                    chunk_index=len(chunks),
                    source_page_number=page,
                    source_section=current_heading
                ))
                buffer = []
                current_page = page

        if buffer:
            chunks.append(DocumentChunkDTO(
                chunk_text="\n\n".join(buffer),
                chunk_index=len(chunks),
                source_page_number=current_page,
                source_section=current_heading
            ))

        # Include tables from general notices (e.g. certification lists)
        for tbl in tables:
            headers = tbl.get("headers", [])
            rows = tbl.get("rows", [])
            page = tbl.get("page_number", 1)
            if not rows:
                continue
            for i in range(0, len(rows), 4):
                sub = rows[i:i + 4]
                r_text = "\n".join(" | ".join(str(c) for c in r if c) for r in sub)
                chunks.append(DocumentChunkDTO(
                    chunk_text=f"Institutional Table Data (Page {page}):\nColumns: {' | '.join(str(h) for h in headers)}\n{r_text}",
                    chunk_index=len(chunks),
                    source_page_number=page,
                    source_section="Structured Table Reference"
                ))

        return chunks


chunking_engine = ChunkingEngine()
