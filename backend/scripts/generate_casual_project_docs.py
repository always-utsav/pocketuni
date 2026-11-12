import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_casual_document():
    doc = docx.Document()

    # Standard simple 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Simple plain dark color, everyday reading font (Calibri)
    COLOR_TEXT = RGBColor(0x22, 0x22, 0x22)
    COLOR_HEADING = RGBColor(0x11, 0x11, 0x11)
    COLOR_CODE = RGBColor(0x33, 0x33, 0x33)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_TEXT
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    def p(text="", bold_prefix=None, space_after=6):
        para = doc.add_paragraph()
        para.paragraph_format.space_after = Pt(space_after)
        para.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = para.add_run(bold_prefix)
            r_b.bold = True
        if text:
            para.add_run(text)
        return para

    def h(text, level=1):
        para = doc.add_paragraph()
        para.paragraph_format.space_before = Pt(14 if level == 1 else 10)
        para.paragraph_format.space_after = Pt(4)
        para.paragraph_format.keep_with_next = True
        run = para.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(14 if level == 1 else 12)
        run.font.color.rgb = COLOR_HEADING
        return para

    def code(text):
        para = doc.add_paragraph()
        para.paragraph_format.space_before = Pt(3)
        para.paragraph_format.space_after = Pt(6)
        para.paragraph_format.left_indent = Inches(0.2)
        para.paragraph_format.line_spacing = 1.1
        lines = text.strip().split('\n')
        for i, line in enumerate(lines):
            r = para.add_run(line + ('\n' if i < len(lines)-1 else ''))
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_CODE
        return para

    def bullet(text, bold_prefix=None):
        para = doc.add_paragraph(style='List Bullet')
        para.paragraph_format.space_after = Pt(3)
        para.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = para.add_run(bold_prefix)
            r_b.bold = True
        if text:
            para.add_run(text)
        return para

    # Title - super casual, no fake banners
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(2)
    r_t = p_title.add_run("Hey!! Here is everything about PocketUni (Read this first)")
    r_t.bold = True
    r_t.font.size = Pt(18)
    r_t.font.color.rgb = COLOR_HEADING

    p("Quick personal notes on what I built, how it works, and how to run it on your laptop without any headache.", space_after=14)

    # A. Intro
    h("A. So... what is PocketUni basically?")
    p("Okay so you know how annoying college stuff at MITS is rn?! Like literally everything is scattered across 10 different places. If you want a syllabus copy, you have to dig through some random 50-page PDF on the college website. If you want to know which room a class got shifted to, you're begging in five different unofficial WhatsApp groups. And don't even get me started on taking leave or getting a bonafide certificate... you literally have to print paper applications, run between department blocks, and pray that the professor is actually sitting in their cabin.")
    
    p("So I decided to just build an all-in-one AI assistant specifically for our college (started with our Centre for AI, and added CSE & IoT too). The whole idea is super simple: you just open the app and ask whatever you want in normal English, like \"what classes do I have tomorrow?\" or \"is Dr. Mausam free at 2 PM?\" or \"draft a medical leave letter for my HOD\".")
    
    p("And the best part is that unlike ChatGPT which usually hallucinates and invents fake college rules, PocketUni actually looks up our real MITS circulars, real timetables, and real faculty profiles before answering. So it actually gives you page numbers and exact links to the real PDFs.")

    # B. Tech stack
    h("B. What tech stack did I use & why? (kept it simple)")
    p("I honestly didn't want to overcomplicate the tech stack with unnecessary buzzwords. I just picked stuff that is fast, reliable, and actually works together without crashing:")
    
    bullet("I used React with Vite for the frontend. React makes the UI super snappy because things update instantly without reloading the whole page. And Vite is genuinely a lifesaver... it starts up the dev server in like 0.3 seconds. No waiting around.", bold_prefix="React 18 & Vite: ")
    bullet("Used this on the frontend because pure JavaScript gets messy real quick. TypeScript catches missing variables, wrong object names, and typos before you even run the code. Saved me tons of debugging time.", bold_prefix="TypeScript: ")
    bullet("Used Tailwind for all styling. I didn't want messy external CSS sheets. Styled it with a clean college vibe — dark navy, subtle teal, and warm paper-like cards so it looks neat.", bold_prefix="Tailwind CSS: ")
    bullet("For the backend API, Python was an obvious choice for AI stuff, and FastAPI is insanely fast. Plus it automatically builds an interactive Swagger test page at /docs which made testing endpoints super easy.", bold_prefix="Python 3.11 & FastAPI: ")
    bullet("This is the main database where everything gets saved permanently — student profiles, faculty data, leave letters, chat history, and audit logs. It's solid, doesn't corrupt data, and handles relational tables easily.", bold_prefix="PostgreSQL 18: ")
    bullet("A clean Python library that lets me talk to Postgres using normal Python code instead of writing raw SQL queries everywhere.", bold_prefix="SQLAlchemy 2: ")
    bullet("This is the AI brain. I used gemini-2.5-flash because it's super quick and smart with college context. And I used gemini-embedding-001 to convert text into mathematical vectors so the search engine understands the *meaning* of your question, not just matching exact keywords.", bold_prefix="Google Gemini AI & Embeddings: ")
    bullet("I used WebSockets so that when a student submits an application, it instantly pops up on the faculty mentor's screen in real time without refreshing! And SSE streams Gemini's answers word-by-word like someone is typing live.", bold_prefix="WebSockets & SSE (Live Streaming): ")
    bullet("Used PyMuPDF (fitz) and python-docx to read real college PDFs and Word documents. Also added openpyxl so the database stays mirrored with an Excel sheet (because college admins still love their Excel files haha).", bold_prefix="Document extractors & Excel Sync: ")

    # C. What works right now
    h("C. What can it actually do right now?")
    p("I spent a lot of time testing this, so what's in the repo right now is actually working (there are 83 automated tests running in the backend and all of them pass green). Here is the breakdown:")

    p("1. Things that are 100% working right now:", bold_prefix="")
    bullet("You can ask about MITS rules, attendance criteria (the 75% rule & medical relaxation), syllabus, hostel timings, library book bank, etc. It quotes official sources with clickable links.", bold_prefix="College Q&A Chatbot: ")
    bullet("Handles casual greetings like \"hi\", \"hello\", \"hey\" warmly with guide options instead of throwing a weird zero-result error.", bold_prefix="Casual Greetings: ")
    bullet("It knows the weekly timetable for B.Tech AI & Robotics, AIML, and AIDS. You can ask what classes you have on Wednesday or whether a professor has free slots.", bold_prefix="Timetable & Class Schedules: ")
    bullet("Full directory for CAI, CSE, and IoT. You can view complete profiles for Dr. Shradha Dubey, Dr. Aftab Ahmed Ansari, Prof. Ramnaresh Sharma, and Dr. Mausam Chouksey with their actual research papers, phone numbers, and cabin hours.", bold_prefix="Faculty Directory: ")
    bullet("This is one of the coolest parts. You can open the Application Agent, chat with it to draft a medical leave or bonafide certificate, pick your faculty mentor (e.g. Dr. Mausam Chouksey), and send it right to their digital inbox. The faculty can hit Approve, Reject, or Request Revision with a note. If they ask for revision, the student sees the note, edits the letter, and resubmits it!", bold_prefix="Digital Leave & Letter Workflow: ")
    bullet("If you log in as Super Admin, you can directly edit student and faculty records in the database, and the changes broadcast live to everyone's screen via WebSockets.", bold_prefix="Admin Management: ")
    bullet("Students can find other classmates based on skills (like PyTorch, ROS, Flutter, C++) if they are looking for teammates for Smart India Hackathon.", bold_prefix="Peer Discovery: ")
    bullet("Direct verified links for Student IMS, Moodle, No Dues, RefRead e-Library, OSM evaluation, and direct DOCX links like the HPC Lab details PDF.", bold_prefix="Verified College Links: ")

    p("2. The Three-Account Sandbox (How to test without signup):", bold_prefix="")
    p("You don't need to create accounts or set up fake passwords. On the home page, just click \"Try Test Sandbox\":")
    bullet("Aarav Sharma (B.Tech student). Use this to test asking questions, checking your timetable, drafting leave letters, and browsing peers.", bold_prefix="Student Sandbox: ")
    bullet("Dr. Mausam Chouksey (Assistant Professor). Use this to check the faculty inbox, approve or reject student letters, and edit consultation hours.", bold_prefix="Faculty Sandbox: ")
    bullet("Utsav Kumawat (Super Admin). Full control over database records, viewing audit logs, and testing document imports.", bold_prefix="Super Admin Sandbox: ")

    p("3. Stuff that depends on setup / config:", bold_prefix="")
    bullet("Real Google OAuth: The code is fully written, but to use real Google login you need your own Google Cloud client ID & secret. The sandbox login bypasses this completely so you don't have to bother with Google Cloud.", bold_prefix="Google Sign-In: ")
    bullet("Gemini API: You need your own free Gemini API key in backend/.env. If you don't add one or if the free daily limit runs out, PocketUni won't crash — its timetable, faculty lookup, portals, and application workflow will still work normally using the local engine.", bold_prefix="Gemini Key: ")

    # D. Next features
    h("D. What can we add next? (Future ideas)")
    p("There's still a bunch of cool stuff we can add whenever we get time:")
    bullet("Right now timetables are seeded from the documents. It would be awesome to add an OCR tool where you just upload a photo of the new semester timetable noticeboard, and AI automatically converts it into database slots.", bold_prefix="Auto Timetable Uploader: ")
    bullet("If the college ever gives API access, we could directly connect to IMS so students can see their exact live attendance percentage and fee dues inside chat.", bold_prefix="Live IMS Integration: ")
    bullet("Multi-level approvals where a leave request goes from Class Mentor -> HOD -> Dean Academics automatically.", bold_prefix="Multi-Step Approvals: ")
    bullet("A lightweight mobile app or PWA that sends phone notifications like \"Hey, your next class is AI Lab in Room 204 in 15 mins\".", bold_prefix="Mobile Notifications: ")
    bullet("Voice support in Hindi and English so you can just talk into your phone while walking to class.", bold_prefix="Voice Queries: ")
    bullet("Adding local offline models (like Llama 3 via Ollama) as an automatic backup for when internet is down or Gemini rate limits hit.", bold_prefix="Offline AI Fallback: ")

    # E. How to run it locally (ZIP guide)
    h("E. How to download & run it on your laptop (Step by step)")
    p("Don't worry about git commands if you don't want to use git. You can literally just download the ZIP and run it:")

    p("Step 1: Download & Unzip", bold_prefix="")
    p("Direct ZIP download link:")
    code("https://github.com/always-utsav/pocketuni/archive/refs/heads/main.zip")
    p("Download it, right click -> Extract All, and open that folder in VS Code.")

    p("Step 2: Check prerequisites", bold_prefix="")
    p("Make sure your laptop has Python, Node, and PostgreSQL installed. Open terminal and check:")
    code("python --version   # needs Python 3.11\nnode -v            # needs Node 20+\nnpm -v             # needs npm 10+\npsql -V            # PostgreSQL (v15 to v18)")

    p("Step 3: Setup your .env file", bold_prefix="")
    p("Inside the backend/ folder, create a file named .env (or copy from backend/.env.example). Put your local Postgres password and your free Gemini key in it:")
    code("DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/pocketuni\nDB_HOST=localhost\nDB_PORT=5432\nDB_USER=postgres\nDB_PASSWORD=YOUR_PASSWORD\nDB_NAME=pocketuni\nSECRET_KEY=my-super-secret-key-12345\nGEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE\nGEMINI_CHAT_MODEL=gemini-2.5-flash\nGEMINI_EMBEDDING_MODEL=gemini-embedding-001\nFRONTEND_ORIGIN=http://localhost:5173")

    p("Step 4: Create the Database in PostgreSQL", bold_prefix="")
    p("Open pgAdmin or terminal and run this one SQL line to make the database:")
    code("CREATE DATABASE pocketuni;")

    p("Step 5: Start the Backend (Terminal 1)", bold_prefix="")
    p("Open terminal inside the PocketUni folder and run:")
    code("# On Windows (PowerShell):\npython -m venv backend\\.venv\n.\\backend\\.venv\\Scripts\\Activate.ps1\n\n# (If on Mac/Linux, run: python3 -m venv backend/.venv && source backend/.venv/bin/activate)\n\n# Install backend packages:\npip install -r backend/requirements.txt\npip install \"psycopg[binary]\" pytest httpx python-multipart python-jose[cryptography] passlib[bcrypt]\n\n# Seed initial MITS college data into Postgres:\npython -m backend.scripts.seed\n\n# Start the server:\nuvicorn backend.app.main:app --reload --port 8000")
    p("Your backend is now running at http://localhost:8000 (and test docs are at http://localhost:8000/docs)!!")

    p("Step 6: Start the Frontend (Terminal 2)", bold_prefix="")
    p("Keep the first terminal running! Open a second terminal in the project folder and run:")
    code("npm install\nnpm run dev")
    p("It will give you a link: http://localhost:5173. Open that in Chrome or Edge!")

    p("Step 7: Try it out!", bold_prefix="")
    p("On the page, click \"Try Test Sandbox\". Pick Student Sandbox to chat and draft letters, or Faculty Sandbox to review applications.")
    p("Pro tip: Open one normal Chrome tab as Student, and open an Incognito window as Faculty. When you submit a leave letter from the student tab, look at the faculty tab — it pops up right away without refreshing!!")

    # F. Troubleshooting
    h("F. Quick troubleshooting (if anything acts up)")
    bullet("Make sure PostgreSQL is actually running on your computer. Also check that your DB_PASSWORD in backend/.env is correct.", bold_prefix="Postgres connection error: ")
    bullet("Windows sometimes blocks running scripts in PowerShell. Just run this once: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass.", bold_prefix="PowerShell script error: ")
    bullet("Make sure your virtual environment was activated (you should see (.venv) at the start of your terminal line).", bold_prefix="ModuleNotFoundError: ")
    bullet("If your free daily Gemini quota gets exhausted, PocketUni won't break. You'll just see a friendly note on AI chat, but timetables, faculty profiles, and leave letters will still work 100%.", bold_prefix="Gemini quota limit (429): ")
    bullet("If port 8000 is taken, start backend with --port 8001. If 5173 is taken, run npm run dev -- --port 3000.", bold_prefix="Port already in use: ")
    p("If you want to run the automated tests to make sure everything is working, just run python -m pytest backend/tests/ -v in your backend terminal. All 83 tests should pass!!")

    # Save directly in root and docs
    root_file = os.path.abspath("PocketUni_Project_Documentation.docx")
    doc.save(root_file)
    print("Saved casual docx to:", root_file)

    docs_file = os.path.abspath("docs/PocketUni_Project_Documentation.docx")
    doc.save(docs_file)
    print("Saved casual docx to:", docs_file)

if __name__ == "__main__":
    create_casual_document()
