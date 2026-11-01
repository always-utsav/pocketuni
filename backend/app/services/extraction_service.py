import os
import time
import io
import shutil
import re
from typing import Dict, List, Any, Optional
import pandas as pd
import openpyxl
from docx import Document as DocxDocument
import pdfplumber
from pypdf import PdfReader
from PIL import Image
import pytesseract
import fitz  # PyMuPDF


class ExtractionResult:
    def __init__(self):
        self.status: str = "COMPLETED"  # COMPLETED, PARTIAL, FAILED
        self.extractor_engine: str = ""
        self.pages_processed: int = 0
        self.tables_found: int = 0
        self.contents: List[Dict[str, Any]] = []
        self.tables: List[Dict[str, Any]] = []
        self.specialized_data: Dict[str, Any] = {}
        self.warnings: List[str] = []
        self.error_message: Optional[str] = None
        self.execution_time_ms: int = 0
        self.ocr_applied: bool = False


class DocumentExtractionEngine:
    def __init__(self):
        # Configure Tesseract path on Windows
        tess_candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
            shutil.which("tesseract") or ""
        ]
        self.tesseract_cmd = next((p for p in tess_candidates if p and os.path.exists(p)), None)
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def extract(self, file_path: str, mime_type: str = "") -> ExtractionResult:
        start_time = time.time()
        result = ExtractionResult()
        _, ext = os.path.splitext(file_path.lower())

        try:
            if ext == ".pdf":
                self._extract_pdf(file_path, result)
            elif ext in [".docx", ".doc"]:
                self._extract_docx(file_path, result)
            elif ext in [".xlsx", ".xls"]:
                self._extract_excel(file_path, result)
            elif ext == ".csv":
                self._extract_csv(file_path, result)
            elif ext == ".txt":
                self._extract_txt(file_path, result)
            elif ext in [".png", ".jpg", ".jpeg"]:
                self._extract_image(file_path, result)
            else:
                result.status = "FAILED"
                result.error_message = f"Unsupported file type for extraction: {ext}"
        except Exception as e:
            result.status = "FAILED"
            result.error_message = f"Extraction failed with error: {str(e)}"
            result.warnings.append(str(e))
        finally:
            result.execution_time_ms = int((time.time() - start_time) * 1000)

        return result

    def _extract_pdf(self, file_path: str, result: ExtractionResult):
        result.extractor_engine = "pdfplumber + pypdf + PyMuPDF OCR"
        scanned_pages = []

        # 1. First pass with pdfplumber for native text & vector tables
        with pdfplumber.open(file_path) as pdf:
            result.pages_processed = len(pdf.pages)
            for idx, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                trimmed = page_text.strip()

                if len(trimmed) < 40:
                    scanned_pages.append(idx)
                else:
                    lines = [ln.strip() for ln in page_text.split("\n") if ln.strip()]
                    for line in lines:
                        is_hd = len(line) < 90 and (
                            line.isupper() or 
                            line.startswith("UNIT-") or 
                            line.startswith("COURSE ") or 
                            line.startswith("ANNEXURE") or
                            line.startswith("RECOMMENDED ")
                        )
                        result.contents.append({
                            "page_number": idx,
                            "heading": line if is_hd else None,
                            "content": line,
                            "content_type": "heading" if is_hd else "paragraph"
                        })

                # Native table extraction
                try:
                    tables = page.extract_tables()
                    for t_idx, tbl in enumerate(tables):
                        if tbl and len(tbl) > 1:
                            # Filter empty rows
                            clean_tbl = [[str(cell).strip() if cell is not None else "" for cell in r] for r in tbl if any(c is not None and str(c).strip() for c in r)]
                            if len(clean_tbl) > 1:
                                headers = clean_tbl[0]
                                rows = clean_tbl[1:]
                                result.tables.append({
                                    "page_number": idx,
                                    "sheet_name": None,
                                    "table_index": t_idx + 1,
                                    "headers": headers,
                                    "rows": rows,
                                    "row_count": len(rows)
                                })
                                result.tables_found += 1
                except Exception as tbl_err:
                    result.warnings.append(f"Page {idx} table extraction note: {str(tbl_err)}")

        # 2. OCR Fallback for scanned/image pages (e.g. Master Timetables)
        if scanned_pages:
            result.ocr_applied = True
            if not self.tesseract_cmd:
                result.status = "PARTIAL"
                result.warnings.append(
                    f"Pages {scanned_pages} contain image-based content, but Tesseract OCR binary was not detected on Windows. "
                    "Install Tesseract at 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' for full OCR parsing."
                )
            else:
                doc = fitz.open(file_path)
                for pno in scanned_pages:
                    try:
                        page = doc[pno - 1]
                        pix = page.get_pixmap(dpi=200)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(img)
                        ocr_lines = [ln.strip() for ln in ocr_text.splitlines() if ln.strip()]
                        
                        for line in ocr_lines:
                            result.contents.append({
                                "page_number": pno,
                                "heading": line if len(line) < 80 and ("TIME TABLE" in line or "Branch" in line or "Faculty" in line) else None,
                                "content": line,
                                "content_type": "ocr_text"
                            })
                        
                        # Layout table extraction on OCR text if reference table
                        if any("Branch" in ln and "Code" in ln for ln in ocr_lines[:5]):
                            self._parse_ocr_course_ref_table(ocr_lines, pno, result)
                        elif any("Faculty Name" in ln for ln in ocr_lines[:5]):
                            self._parse_ocr_faculty_ref_table(ocr_lines, pno, result)
                        elif any("Master Time Table" in ln or "TUE" in ln for ln in ocr_lines[:5]):
                            self._parse_ocr_timetable_grid(ocr_lines, pno, result)
                    except Exception as ocr_err:
                        result.warnings.append(f"Page {pno} OCR processing error: {str(ocr_err)}")
                doc.close()

        # 3. Post-process specialized datasets
        self._analyze_specialized_documents(file_path, result)

    def _parse_ocr_course_ref_table(self, lines: List[str], pno: int, result: ExtractionResult):
        """Extracts structured course codes from timetable reference tables."""
        courses = []
        for line in lines:
            m = re.match(r'^(AI|AIDS|AIML|AIR)\s*\|\s*(\d{7,8}[A-Za-z0-9]*)\s*\|\s*(.+)$', line)
            if m:
                courses.append({
                    "branch": m.group(1),
                    "code": m.group(2),
                    "name": m.group(3).strip()
                })
        if courses:
            result.tables.append({
                "page_number": pno,
                "sheet_name": "Course Reference",
                "table_index": 1,
                "headers": ["Branch", "Code", "Course Name"],
                "rows": [[c["branch"], c["code"], c["name"]] for c in courses],
                "row_count": len(courses)
            })
            result.tables_found += 1
            result.specialized_data.setdefault("course_codes", []).extend(courses)

    def _parse_ocr_faculty_ref_table(self, lines: List[str], pno: int, result: ExtractionResult):
        """Extracts faculty code mapping (e.g. MC -> Dr. Mausam Chouksey)."""
        faculty_map = {}
        for line in lines:
            matches = re.findall(r'(?:Dr\.|Mr\.|Mrs\.|Ms\.)\s+[A-Za-z\s\.]+\s+([A-Z]{2,4})\b', line)
            # Match "Faculty Name | Code" pattern
            m = re.match(r'^(?:Dr\.|Mr\.|Mrs\.|Ms\.)\s+([A-Za-z\s\.]+)\s+([A-Z]{2,4})$', line)
            if m:
                faculty_map[m.group(2)] = m.group(1).strip()
        if faculty_map:
            result.specialized_data.setdefault("faculty_codes", {}).update(faculty_map)

    def _parse_ocr_timetable_grid(self, lines: List[str], pno: int, result: ExtractionResult):
        """Extracts timetable session and schedule markers."""
        tt_info = {"session": "July-Dec 2026", "slots": []}
        for line in lines:
            if "W.E.F" in line:
                m = re.search(r'W\.E\.F\s*([0-9\.]+)', line)
                if m:
                    tt_info["effective_date"] = m.group(1)
            elif any(day in line for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT"]):
                tt_info["slots"].append(line)
        result.specialized_data.setdefault("timetable_overview", tt_info)

    def _analyze_specialized_documents(self, file_path: str, result: ExtractionResult):
        fname = os.path.basename(file_path).lower()

        # A. Internal Marks Analysis & Reconciliation
        if "minor" in fname and "marks" in fname:
            marks_records = []
            for tbl in result.tables:
                headers = [h.replace("\n", " ").strip() for h in tbl["headers"]]
                enroll_idx = next((i for i, h in enumerate(headers) if "enrollment" in h.lower()), None)
                name_idx = next((i for i, h in enumerate(headers) if "name" in h.lower()), None)
                
                if enroll_idx is not None and name_idx is not None:
                    for row in tbl["rows"]:
                        if len(row) > max(enroll_idx, name_idx):
                            enroll = row[enroll_idx].strip()
                            name = row[name_idx].strip()
                            if enroll and not enroll.lower().startswith("enroll"):
                                marks_records.append({
                                    "enrollment_number": enroll,
                                    "student_name": name,
                                    "total_columns": len(row)
                                })
            result.specialized_data["internal_marks_summary"] = {
                "records_extracted": len(marks_records),
                "is_confidential": True,
                "reconciliation_required": True,
                "note": "Confidential academic records. Restricted to Super Admin review."
            }

        # B. Professional Certifications
        elif "professional_certification" in fname:
            certs = []
            for tbl in result.tables:
                headers = [h.lower() for h in tbl["headers"]]
                if any("course" in h for h in headers) or any("duration" in h for h in headers):
                    for row in tbl["rows"]:
                        if len(row) >= 3 and row[1]:
                            certs.append({
                                "course_name": row[1],
                                "duration": row[2] if len(row) > 2 else "",
                                "link": row[3] if len(row) > 3 else ""
                            })
            result.specialized_data["professional_certifications"] = certs

    def _extract_docx(self, file_path: str, result: ExtractionResult):
        result.extractor_engine = "python-docx"
        doc = DocxDocument(file_path)
        result.pages_processed = 1

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            is_heading = para.style.name.startswith("Heading") or (len(text) < 80 and text.isupper())
            result.contents.append({
                "page_number": 1,
                "heading": text if is_heading else None,
                "content": text,
                "content_type": "heading" if is_heading else "paragraph"
            })

        for t_idx, table in enumerate(doc.tables):
            all_rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
            if all_rows:
                result.tables.append({
                    "page_number": 1,
                    "sheet_name": None,
                    "table_index": t_idx + 1,
                    "headers": all_rows[0],
                    "rows": all_rows[1:],
                    "row_count": len(all_rows[1:])
                })
                result.tables_found += 1

    def _extract_excel(self, file_path: str, result: ExtractionResult):
        result.extractor_engine = "openpyxl + pandas"
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet_names = wb.sheetnames
        result.pages_processed = len(sheet_names)

        for s_idx, name in enumerate(sheet_names):
            ws = wb[name]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue

            clean_rows = []
            for r in rows:
                if any(v is not None for v in r):
                    clean_rows.append([str(v).strip() if v is not None else "" for v in r])

            if clean_rows:
                headers = clean_rows[0]
                data_rows = clean_rows[1:] if len(clean_rows) > 1 else []
                result.tables.append({
                    "page_number": s_idx + 1,
                    "sheet_name": name,
                    "table_index": 1,
                    "headers": headers,
                    "rows": data_rows,
                    "row_count": len(data_rows)
                })
                result.tables_found += 1

    def _extract_csv(self, file_path: str, result: ExtractionResult):
        result.extractor_engine = "pandas (csv)"
        df = pd.read_csv(file_path, dtype=str).fillna("")
        result.pages_processed = 1
        headers = list(df.columns)
        rows = df.values.tolist()
        result.tables.append({
            "page_number": 1,
            "sheet_name": None,
            "table_index": 1,
            "headers": headers,
            "rows": rows,
            "row_count": len(rows)
        })
        result.tables_found = 1

    def _extract_txt(self, file_path: str, result: ExtractionResult):
        result.extractor_engine = "python-text"
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        result.pages_processed = 1
        for idx, ln in enumerate(lines, start=1):
            result.contents.append({
                "page_number": 1,
                "heading": ln if len(ln) < 80 and ln.isupper() else None,
                "content": ln,
                "content_type": "paragraph"
            })

    def _extract_image(self, file_path: str, result: ExtractionResult):
        result.extractor_engine = "Pillow + pytesseract"
        result.pages_processed = 1
        result.ocr_applied = True
        if not self.tesseract_cmd:
            result.status = "FAILED"
            result.error_message = "Tesseract OCR binary not found on Windows."
            return

        img = Image.open(file_path)
        ocr_text = pytesseract.image_to_string(img)
        lines = [ln.strip() for ln in ocr_text.splitlines() if ln.strip()]
        for ln in lines:
            result.contents.append({
                "page_number": 1,
                "heading": ln if len(ln) < 80 and ln.isupper() else None,
                "content": ln,
                "content_type": "ocr_text"
            })


extraction_engine = DocumentExtractionEngine()
