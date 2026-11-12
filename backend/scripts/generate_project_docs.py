import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = docx.Document()

    # 1. Page Margins (Standard 1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # Palette
    COLOR_PRIMARY = RGBColor(0x14, 0x25, 0x2B)   # Deep Midnight Navy
    COLOR_TEAL = RGBColor(0x17, 0x6B, 0x68)      # Forest Teal
    COLOR_COPPER = RGBColor(0xB9, 0x6D, 0x47)    # Warm Copper
    COLOR_CHARCOAL = RGBColor(0x27, 0x32, 0x38)  # Body text
    COLOR_MUTED = RGBColor(0x52, 0x62, 0x6B)     # Secondary / Muted

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_CHARCOAL
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(5)

    def add_title(text, subtitle_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(21)
        run.bold = True
        run.font.color.rgb = COLOR_PRIMARY

        p_sub = doc.add_paragraph()
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(16)
        r_sub = p_sub.add_run(subtitle_text)
        r_sub.font.name = 'Calibri'
        r_sub.font.size = Pt(10.5)
        r_sub.italic = True
        r_sub.font.color.rgb = COLOR_MUTED

    def add_heading1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(14.5)
        run.bold = True
        run.font.color.rgb = COLOR_PRIMARY

    def add_heading2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.bold = True
        run.font.color.rgb = COLOR_TEAL

    def add_heading3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.bold = True
        run.font.color.rgb = COLOR_COPPER

    def add_body(text, bold_prefix=None, space_after=5):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_PRIMARY
        r_text = p.add_run(text)
        r_text.font.color.rgb = COLOR_CHARCOAL
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_PRIMARY
        r_text = p.add_run(text)
        r_text.font.color.rgb = COLOR_CHARCOAL
        return p

    def add_code_block(code_text, label=None):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        # Background color: warm porcelain/light gray #F5F3EE
        shading = parse_xml(r'<w:shd {} w:fill="F5F3EE"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading)

        # Thin light border
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(r'''
            <w:tcBorders {} >
                <w:top w:val="single" w:sz="4" w:space="0" w:color="D9CFBF"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="D9CFBF"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="D9CFBF"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="D9CFBF"/>
            </w:tcBorders>
        '''.format(nsdecls('w')))
        tcPr.append(tcBorders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.1

        if label:
            r_lbl = p.add_run(f"# {label}\n")
            r_lbl.font.name = 'Consolas'
            r_lbl.font.size = Pt(8.5)
            r_lbl.font.color.rgb = COLOR_MUTED
            r_lbl.italic = True

        lines = code_text.strip().split('\n')
        for i, line in enumerate(lines):
            r = p.add_run(line + ('\n' if i < len(lines)-1 else ''))
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_PRIMARY

        # Add small spacing after table
        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(4)

    def add_callout(text, bold_prefix="Note: "):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        shading = parse_xml(r'<w:shd {} w:fill="EEF2ED"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading)

        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(r'''
            <w:tcBorders {} >
                <w:top w:val="none"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="176B68"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:tcBorders>
        '''.format(nsdecls('w')))
        tcPr.append(tcBorders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_TEAL

        r_text = p.add_run(text)
        r_text.font.size = Pt(10)
        r_text.font.color.rgb = COLOR_CHARCOAL

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(4)

    # ------------------ DOCUMENT CONTENT ------------------

    # Title & Subtitle
    add_title(
        "PocketUni — MITS Gwalior AI College Assistant",
        "Project Architecture, Implementation Details & Local Run Guide | By Utsav Kumawat"
    )

    # SECTION A
    add_heading1("A. Introduction — What is PocketUni?")
    
    add_body(
        "I built PocketUni to solve a problem that every single student and professor at Madhav Institute "
        "of Technology & Science (MITS-DU), Gwalior experiences daily: college information is scattered "
        "all over the place!! Academic circulars sit buried inside 50-page PDFs on the college website, timetable updates "
        "get forwarded across ten different unofficial WhatsApp groups, nobody knows which classroom a professor is in "
        "during their consultation hours, and submitting something as basic as a medical leave letter or bonafide certificate "
        "still involves printing paper forms and running up and down the academic blocks to track down mentors."
    )

    add_body(
        "The idea behind PocketUni was pretty simple: create a centralized, conversational AI assistant specifically "
        "customized for MITS Gwalior (starting with the Centre for Artificial Intelligence and expanding to Computer Science "
        "and IoT). Instead of digging through multiple portals, a student or faculty member can simply open one application "
        "and ask natural questions like \"What classes do I have tomorrow morning?\", \"Is Dr. Mausam Chouksey free at 2 PM?\", "
        "or \"Draft an official leave application for the HOD\". Crucially, it doesn't make up random college rules — it cites "
        "real institutional documents, real timetables, and official portal links."
    )

    # SECTION B
    add_heading1("B. Technology Stack — What did I use and why?")

    add_body(
        "When putting this project together, I wanted a modern, fast, and rock-solid stack that could handle real-time "
        "interactions, document retrieval, and complex academic logic without unnecessary overhead. Here is what I chose and why:"
    )

    add_bullet(
        "I chose React with Vite because the frontend needs to be snappy. Everything re-renders smoothly without "
        "jarring page reloads, and Vite starts the local development server almost instantaneously (well under a second).",
        bold_prefix="React 18 & Vite (Frontend): "
    )

    add_bullet(
        "I used TypeScript across the entire client side. Defining strict types for students, faculty profiles, applications, "
        "and chat messages prevented dozens of annoying runtime bugs, typos, and mismatched JSON keys before the code ever ran.",
        bold_prefix="TypeScript: "
    )

    add_bullet(
        "Used for the visual identity. Instead of writing bloated CSS sheets, I used Tailwind to build a clean, institutional "
        "palette with deep midnight navy, forest teal, warm porcelain card surfaces, and subtle terracotta accents matching the college look.",
        bold_prefix="Tailwind CSS & Lucide Icons: "
    )

    add_bullet(
        "FastAPI is the backbone of the backend. I went with it because it is asynchronous, blazing fast, automatically validates "
        "request payloads with Pydantic, and generates interactive Swagger documentation (/docs) right out of the box.",
        bold_prefix="Python 3.11 & FastAPI (Backend API): "
    )

    add_bullet(
        "I used PostgreSQL 18 as the permanent relational database. It stores users, faculty publications, student profiles, "
        "formal applications, status histories, and immutable audit logs with complete transactional integrity.",
        bold_prefix="PostgreSQL 18 & SQLAlchemy 2: "
    )

    add_bullet(
        "Used for database schema versioning. It allows the database schema to evolve safely without having to drop tables or lose data.",
        bold_prefix="Alembic (Database Migrations): "
    )

    add_bullet(
        "For conversational intelligence, I integrated the official Google GenAI SDK. The chat runs on gemini-2.5-flash for fast reasoning, "
        "while text chunks are converted into 3,072-dimensional vectors using gemini-embedding-001 so queries find relevant documents by meaning, not just keywords.",
        bold_prefix="Google Gemini AI & Embeddings: "
    )

    add_bullet(
        "I implemented WebSockets so events (like a student submitting a leave request or an admin editing a profile) "
        "instantly ping other logged-in tabs. Server-Sent Events (SSE) are used on /chat/conversations/{id}/stream to stream Gemini's answer token-by-token.",
        bold_prefix="WebSockets & Server-Sent Events (SSE): "
    )

    add_bullet(
        "I used PyMuPDF (fitz), pdfplumber, and python-docx to ingest official documents (like the Centre for AI DOCX curriculum file). "
        "I also used openpyxl to maintain a two-way synchronized Excel spreadsheet mirror of student and faculty rosters for administrative record-keeping.",
        bold_prefix="Document Processing (PDF, DOCX, Excel): "
    )

    add_bullet(
        "JWT tokens with HS256 encryption handle session security. Google OAuth 2.0 endpoints are integrated for institutional domain sign-in, "
        "and a built-in Three-Account Sandbox lets anyone test the platform immediately without needing credentials.",
        bold_prefix="Authentication & Sandbox Engine: "
    )

    # SECTION C
    add_heading1("C. What can PocketUni actually do right now?")

    add_body(
        "I made sure that what is written in the repository actually works. The current implementation has 83 passing automated "
        "tests and covers the following concrete workflows:"
    )

    add_heading2("1. Fully Implemented & Working Capabilities")

    add_bullet(
        "Answers student questions with exact source citations, page numbers, and direct PDF links. If someone sends a casual greeting like \"hi\" or \"who are you\", it answers warmly rather than spitting out a zero-result search error.",
        bold_prefix="Institutional AI Chatbot & Intent Router: "
    )

    add_bullet(
        "Contains schedule data for B.Tech AI & Robotics, AIML, and AIDS. Students can ask about lecture timings, subject codes, room locations, or check whether specific professors have free slots for consultations.",
        bold_prefix="Timetable & Schedule Intelligence: "
    )

    add_bullet(
        "Searchable directory with filters for CAI, CSE, and IoT. Shows rich profiles for professors (such as Dr. Shradha Dubey, Dr. Aftab Ahmed Ansari, Prof. Ramnaresh Sharma, and Dr. Mausam Chouksey) including verified research publications, consultation hours, and phone numbers.",
        bold_prefix="Official Faculty Directory & Verified Profiles: "
    )

    add_bullet(
        "Students can draft Indian academic letters (medical leave, bonafide certificates, duty leaves) using an interactive slot-filling chat agent. The letter is digitally shared with the mentor's inbox, where faculty can Approve, Reject, or Request Revisions. If revisions are requested, the student can edit and resubmit directly.",
        bold_prefix="Digital Application & Review Lifecycle: "
    )

    add_bullet(
        "Direct portal for institutional admins to inspect database health, view immutable audit trails, tune RAG retrieval thresholds, download Excel roster mirrors, and live-edit canonical student and faculty records with instant WebSocket sync.",
        bold_prefix="Super Admin Management Portal: "
    )

    add_bullet(
        "Allows students to discover peers by technical skills (Python, ROS, PyTorch, Flutter) for Smart India Hackathons and engineering projects while respecting privacy controls.",
        bold_prefix="Peer Student Discovery: "
    )

    add_bullet(
        "Directly resolves exact institutional URLs for student services (Integrated Management System - IMS, Moodle LMS, No Dues Clearance, OSM Evaluation, RefRead e-Library) and official curriculum PDFs extracted from the Centre for AI DOCX.",
        bold_prefix="Verified Portal & Document Resolution: "
    )

    add_heading2("2. The Three-Account Sandbox")
    add_body(
        "To make testing seamless without requiring separate email signups or real Google accounts, I built a Three-Account Sandbox accessible right from the landing page:"
    )

    add_bullet(
        "Lead administrator role (Utsav Kumawat). Has full authority to inspect tables, review documents, calibrate search thresholds, and edit canonical profile records in PostgreSQL.",
        bold_prefix="Super Admin Sandbox: "
    )

    add_bullet(
        "Third-year B.Tech undergraduate (Aarav Sharma). Can ask academic questions, check class schedules, draft leave applications, submit requests to faculty mentors, and browse peer skill profiles.",
        bold_prefix="Student Sandbox: "
    )

    add_bullet(
        "Assistant Professor & Academic Mentor (Dr. Mausam Chouksey). Receives student leave requests in real time, requests revisions, approves/rejects letters, and manages office consultation hours.",
        bold_prefix="Faculty Sandbox: "
    )

    add_heading2("3. Implemented but Dependent on External Configuration")
    add_bullet(
        "The OAuth endpoints and token callbacks are fully written in backend/app/api/v1/routes/auth.py, but actually logging in with a live Google account requires registering an OAuth Client ID and Secret in Google Cloud Console and adding authorized redirect URIs. The sandbox login bypasses this so anyone can run the app locally.",
        bold_prefix="Live Google OAuth 2.0: "
    )
    add_bullet(
        "Generative answering and streaming work out of the box if GEMINI_API_KEY is supplied in backend/.env. If the key is omitted or the daily free quota runs out, PocketUni automatically falls back to its deterministic intent engine and local institutional retrieval.",
        bold_prefix="Gemini Generative Synthesis: "
    )

    # SECTION D
    add_heading1("D. What can be added next?")

    add_body(
        "PocketUni currently covers the core academic and administrative workflows, but there's a lot of exciting ground "
        "left to expand into in the future. Realistic roadmap items include:"
    )

    add_bullet(
        "Adding an automated OCR and vision pipeline so when the academic section publishes new semester timetables as images or scanned circulars, the system automatically parses lecture slots into database rows.",
        bold_prefix="Automated Timetable Ingestion: "
    )

    add_bullet(
        "Where authorized by college administration, building secure connectors to the college IMS portal to pull real-time individual attendance percentages, internal marks, and fee payment receipts directly into the chat.",
        bold_prefix="Direct IMS & ERP Integration: "
    )

    add_bullet(
        "Extending the application engine to support multi-stage academic approvals (e.g. Class Mentor -> Head of Department -> Dean Academics) with printable PDF generation carrying digital verification stamps.",
        bold_prefix="Multi-Tier Departmental Workflows: "
    )

    add_bullet(
        "Packaging the frontend as a Progressive Web App (PWA) or lightweight mobile app with push notifications reminding students 15 minutes before an upcoming lecture or lab session.",
        bold_prefix="Mobile Experience & Push Notifications: "
    )

    add_bullet(
        "Adding voice input in Hindi and English so students can ask timetable or room queries on the go without typing.",
        bold_prefix="Bilingual Voice Assistant: "
    )

    add_bullet(
        "Supporting local open-source models (such as Llama 3 or Mistral via Ollama) alongside Gemini as an automatic fallback when internet connectivity is spotty or API rate limits are hit.",
        bold_prefix="Local Model Fallback: "
    )

    # SECTION E
    add_heading1("E. How to download and run PocketUni")

    add_body(
        "I've made sure PocketUni can be set up and run completely on a local laptop or workstation without Docker. "
        "Here is the exact step-by-step procedure starting from downloading the ZIP from GitHub:"
    )

    add_heading2("Step 1 — Download and extract")
    add_body(
        "You can download the entire repository as a single ZIP archive directly from GitHub using this link:\n"
        "https://github.com/always-utsav/pocketuni/archive/refs/heads/main.zip\n\n"
        "Extract the downloaded ZIP file onto your machine (for example, C:\\PocketUni on Windows or ~/PocketUni on macOS/Linux). "
        "Then open that extracted folder in Visual Studio Code (or your preferred terminal)."
    )

    add_heading2("Step 2 — Verify Prerequisites")
    add_body(
        "Make sure you have the following installed on your system. You can check their versions from your terminal:"
    )
    add_code_block(
        "node -v          # Needs Node.js 20.x or higher\n"
        "npm -v           # Needs npm 10.x or higher\n"
        "python --version # Needs Python 3.11.x\n"
        "psql -V          # PostgreSQL 15, 16, 17 or 18",
        label="Terminal version check"
    )

    add_heading2("Step 3 — Environment Configuration")
    add_body(
        "Inside the backend/ folder, create a file named .env (you can copy backend/.env.example). Fill in your local "
        "PostgreSQL connection details and your free Google Gemini API key (from aistudio.google.com). Do not commit your real secrets to Git!!"
    )
    add_code_block(
        "# backend/.env\n"
        "DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/pocketuni\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "DB_USER=postgres\n"
        "DB_PASSWORD=YOUR_PASSWORD\n"
        "DB_NAME=pocketuni\n"
        "SECRET_KEY=your-custom-secret-key-for-local-dev-2026\n"
        "GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE\n"
        "GEMINI_CHAT_MODEL=gemini-2.5-flash\n"
        "GEMINI_EMBEDDING_MODEL=gemini-embedding-001\n"
        "FRONTEND_ORIGIN=http://localhost:5173",
        label="Sample backend/.env configuration"
    )

    add_heading2("Step 4 — Database Setup")
    add_body(
        "1. Open your PostgreSQL terminal (psql -U postgres) or pgAdmin and create the fresh database:\n"
        "   CREATE DATABASE pocketuni;\n"
        "2. To apply database tables and seed verified MITS institutional data (faculty profiles, departments, timetables, and courses), "
        "run the seed script inside your Python environment as shown in Step 5. (If connecting to an existing database, you only need to run alembic upgrade head)."
    )

    add_heading2("Step 5 — Start the Backend (Terminal 1)")
    add_body(
        "Open a terminal in the project root and run the following commands:"
    )

    add_code_block(
        "# 1. Create and activate Python virtual environment\n"
        "# On Windows (PowerShell):\n"
        "python -m venv backend\\.venv\n"
        ".\\backend\\.venv\\Scripts\\Activate.ps1\n"
        "# On macOS / Linux (Terminal):\n"
        "# python3 -m venv backend/.venv && source backend/.venv/bin/activate\n\n"
        "# 2. Install Python dependencies\n"
        "pip install --upgrade pip\n"
        "pip install -r backend/requirements.txt\n"
        "pip install \"psycopg[binary]\" pytest httpx python-multipart python-jose[cryptography] passlib[bcrypt]\n\n"
        "# 3. Seed initial institutional data into PostgreSQL (safe, fresh setup)\n"
        "python -m backend.scripts.seed\n\n"
        "# 4. Start FastAPI server\n"
        "uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000",
        label="Terminal 1 — Backend startup"
    )
    add_body(
        "The backend API will now be running at http://localhost:8000. You can view the interactive API documentation at http://localhost:8000/docs."
    )

    add_heading2("Step 6 — Start the Frontend (Terminal 2)")
    add_body(
        "Open a second terminal window in the project root and start the React Vite client:"
    )
    add_code_block(
        "# Install frontend npm dependencies\n"
        "npm install\n\n"
        "# Start Vite development server\n"
        "npm run dev",
        label="Terminal 2 — Frontend startup"
    )
    add_body(
        "The frontend will be live at http://localhost:5173."
    )

    add_heading2("Step 7 — Login and Explore")
    add_body(
        "Open your browser and navigate to http://localhost:5173. On the landing page, click \"Try Test Sandbox\". "
        "You can pick any of the three roles (Student, Faculty, or Super Admin) and test immediately without needing passwords or verification emails.\n\n"
        "Tip for testing real-time workflows: Open one normal browser tab as the Student Sandbox, and an Incognito window as the Faculty Sandbox. "
        "Draft and share a leave application from the student tab — it will show up inside the faculty inbox instantly via WebSockets without needing a page refresh!!"
    )

    # SECTION F
    add_heading1("F. Small troubleshooting section")

    add_body(
        "If you run into any hiccups while setting things up, here are quick solutions to the most common issues:"
    )

    add_bullet(
        "Ensure the local PostgreSQL service is started in Windows Services or your OS service manager. Also check that DB_NAME, DB_USER, and DB_PASSWORD in backend/.env match your PostgreSQL installation.",
        bold_prefix="PostgreSQL Connection Error: "
    )

    add_bullet(
        "If PowerShell blocks activating the virtual environment, run this once in PowerShell: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass.",
        bold_prefix="PowerShell Script Execution Policy: "
    )

    add_bullet(
        "If you see ModuleNotFoundError: No module named 'psycopg', make sure you activated the virtual environment and ran pip install \"psycopg[binary]\".",
        bold_prefix="Missing Python Dependencies: "
    )

    add_bullet(
        "If your free Gemini quota runs out or rate limits hit (429), PocketUni does not crash!! Deterministic features (timetables, faculty availability, formal applications, portal links) keep running normally, while AI responses will display a polite notice informing you that the quota is temporarily resting.",
        bold_prefix="Gemini API Quota Exhaustion: "
    )

    add_bullet(
        "If port 8000 is occupied, launch backend with uvicorn backend.app.main:app --reload --port 8001. If port 5173 is occupied, run npm run dev -- --port 3000.",
        bold_prefix="Port Conflicts: "
    )

    add_callout(
        "To verify that everything is working properly on your machine, you can run the complete automated test suite anytime by running "
        "python -m pytest backend/tests/ -v inside your backend virtual environment. All 83 tests should pass green!",
        bold_prefix="Pro Tip: "
    )

    # Save document in project root
    output_path = os.path.abspath("PocketUni_Project_Documentation.docx")
    doc.save(output_path)
    print(f"Document saved successfully to: {output_path}")

    # Also save a copy in docs/ for version control
    docs_copy_path = os.path.abspath("docs/PocketUni_Project_Documentation.docx")
    doc.save(docs_copy_path)
    print(f"Copy saved successfully to: {docs_copy_path}")

    return output_path

if __name__ == "__main__":
    create_document()
