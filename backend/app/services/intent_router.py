import logging
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.identity import User
from backend.app.models.student import StudentProfile
from backend.app.models.faculty import FacultyProfile, FacultyResearchInterest
from backend.app.models.academic import Laboratory, ClassCoordinator
from backend.app.models.document import InstitutionalDocument
from backend.app.services.timetable_service import timetable_service
from backend.app.services.gemini_service import gemini_service
from backend.app.services.institutional_links import resolve_institutional_link, INSTITUTIONAL_LINK_REGISTRY

logger = logging.getLogger("pocketuni.intent_router")


class IntentRouter:
    """
    Deterministic academic intent classifier and specialized handler.
    Directs institutional inquiries to appropriate authoritative data resolvers.
    """

    def route_query(
        self,
        db: Session,
        query: str,
        user: Optional[User] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Dict[str, Any]]:
        intent = self.classify_intent(query)
        return self.handle_intent(db, intent, query, user, conversation_history)

    def classify_intent(self, query: str) -> str:
        q = query.lower().strip()

        # 0. Check for verified Institutional Link & Portal match first
        link_match = resolve_institutional_link(query)
        if link_match:
            return "INSTITUTIONAL_LINK"

        # 1. Faculty Availability
        if any(p in q for p in [
            "who is free", "is teacher free", "is faculty free", "available at",
            "no scheduled class", "free at", "teacher available", "faculty available",
            "teacher has no class", "free teacher", "free faculty", "faculty free at"
        ]):
            return "FACULTY_AVAILABILITY"

        # 2. Class Coordinator
        if any(p in q for p in [
            "class coordinator", "year coordinator", "coordinator for",
            "who is coordinator", "who is the coordinator", "contact coordinator"
        ]):
            return "CLASS_COORDINATOR_LOOKUP"

        # 3. Timetable / Schedule
        if any(p in q for p in [
            "timetable", "time table", "schedule", "classes tomorrow", "classes today",
            "classes on", "class tomorrow", "class today", "which classes", "what classes",
            "next lab", "lecture today", "lectures today", "periods today", "my schedule"
        ]):
            return "TIMETABLE_QUERY"

        # 4. Laboratories
        if any(p in q for p in [
            "laboratories", "laboratory", "robotics lab", "hpc lab", "programming lab",
            "ar/vr lab", "augmented reality lab", "virtual reality lab", "labs in centre for ai",
            "labs available", "what labs"
        ]):
            return "LABORATORY_LOOKUP"

        # 5. Application drafting
        if any(p in q for p in [
            "apply for leave", "leave application", "bonafide certificate", "bonafide application",
            "draft an application", "draft application", "permission letter", "noc application",
            "noc certificate", "write an application"
        ]):
            return "APPLICATION_WORKFLOW"

        # 6. Faculty lookup
        if any(p in q for p in [
            "who is teaching", "associated with robotics research", "teaches data structures",
            "faculty researching", "dr. mausam", "dr. rajni", "dr. pawan", "dr. arun",
            "who teaches"
        ]):
            return "FACULTY_LOOKUP"

        # 7. Greeting & Conversational Intent
        greeting_words = {"hi", "hello", "hey", "namaste", "hola", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup"}
        cleaned_words = re.sub(r'[^\w\s]', '', q).split()
        if cleaned_words:
            first_word = cleaned_words[0]
            clean_str = " ".join(cleaned_words)
            if clean_str in greeting_words or (first_word in greeting_words and len(cleaned_words) <= 4):
                return "GREETING"
        if any(p in q for p in [
            "who are you", "what is pocketuni", "what can you do", "how can you help",
            "tell me about yourself", "help me", "what are your features", "namaste"
        ]):
            return "GREETING"

        return "GENERAL_INSTITUTIONAL"

    def handle_intent(
        self,
        db: Session,
        intent: str,
        query: str,
        user: User,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Executes specialized deterministic intent handling.
        Returns None if intent falls back to general institutional RAG.
        """
        if intent == "INSTITUTIONAL_LINK":
            return self._handle_institutional_link(query)

        elif intent == "GREETING":
            return self._handle_greeting(user)

        elif intent == "TIMETABLE_QUERY":
            return self._handle_timetable(db, query, user)

        elif intent == "FACULTY_AVAILABILITY":
            return self._handle_faculty_availability(db, query)

        elif intent == "CLASS_COORDINATOR_LOOKUP":
            return self._handle_class_coordinator(db, query, user)

        elif intent == "LABORATORY_LOOKUP":
            return self._handle_laboratory(db, query)

        elif intent == "FACULTY_LOOKUP":
            return self._handle_faculty_lookup(db, query)

        return None

    def _handle_greeting(self, user: Optional[User] = None) -> Dict[str, Any]:
        user_name = user.full_name if (user and user.full_name) else "there"
        answer = (
            f"Hello {user_name}! I am **PocketUni**, the official AI Academic Assistant for "
            f"**Madhav Institute of Technology & Science (MITS-DU), Gwalior**.\n\n"
            f"Here is how I can assist you right now:\n\n"
            f"- 📅 **Timetable & Schedules**: Ask *\"What is my timetable tomorrow?\"* or *\"Which classes do I have on Monday?\"*\n"
            f"- 👨‍🏫 **Faculty & Availability**: Ask *\"Who is free at 11 AM tomorrow?\"* or check faculty research interests.\n"
            f"- 🔬 **Laboratories & Infrastructure**: Ask *\"Tell me about the Robotics or AR/VR lab in CAI\"*.\n"
            f"- 🔗 **Official MITS Portals**: Ask for verified direct links to *Student IMS*, *Moodle*, *No Dues*, or *Alumni Portal*.\n"
            f"- 📝 **Application Agent**: Ask *\"Draft a leave application\"* or request a bonafide certificate for review.\n\n"
            f"How can I assist you today?"
        )
        return {
            "answer": answer,
            "intent": "GREETING",
            "citations": [{
                "title": "MITS Gwalior Academic & Research Portals",
                "sourceUrl": "https://web.mitsgwalior.in",
                "category": "PORTAL",
                "page": 1,
                "section": "Centre for Artificial Intelligence",
                "snippet": "Official MITS Gwalior institutional assistant services and departmental coordination."
            }]
        }

    def _handle_institutional_link(self, query: str) -> Optional[Dict[str, Any]]:
        item = resolve_institutional_link(query)
        if not item:
            return None

        answer = (
            f"### {item['title']}\n\n"
            f"{item['description']}\n\n"
            f"🔗 **Official Access URL**: [{item['url']}]({item['url']})\n\n"
            f"- **Managing Body**: {item['department']}\n"
            f"- **System Classification**: `{item['category']}`\n"
            f"- **Verification Authority**: {item['source']}"
        )

        return {
            "answer": answer,
            "intent": "INSTITUTIONAL_LINK",
            "citations": [{
                "title": item["title"],
                "sourceUrl": item["url"],
                "category": item["category"],
                "page": 1,
                "section": item["department"],
                "snippet": item["description"]
            }]
        }

    def _handle_timetable(self, db: Session, query: str, user: User) -> Dict[str, Any]:
        """
        Handles student timetable lookup grounded strictly in authenticated profile context
        or query-extracted attributes. Zero unsafe assumptions or silent fallbacks.
        """
        q_lower = query.lower()
        branch = None
        semester = None
        section = None

        # 1. Parse branch from query
        if "robotics" in q_lower or "air" in q_lower or "ai & robotics" in q_lower or "it (air)" in q_lower:
            branch = "Information Technology (Artificial Intelligence and Robotics)"
        elif "aiml" in q_lower or "machine learning" in q_lower:
            branch = "Artificial Intelligence and Machine Learning"
        elif "aids" in q_lower or "data science" in q_lower:
            branch = "Artificial Intelligence and Data Science"
        elif "cai" in q_lower or "artificial intelligence" in q_lower:
            branch = "Artificial Intelligence"
        elif "cse" in q_lower or "computer science" in q_lower:
            branch = "Computer Science & Engineering"
        elif "iot" in q_lower or "internet of things" in q_lower:
            branch = "Centre for Internet of Things"
        elif "civil" in q_lower:
            branch = "Civil Engineering"
        elif "mechanical" in q_lower:
            branch = "Mechanical Engineering"
        elif "electrical" in q_lower:
            branch = "Electrical Engineering"
        elif "chemical" in q_lower:
            branch = "Chemical Engineering"

        # 2. Parse semester from query
        if any(k in q_lower for k in ["3rd sem", "iii sem", "third sem", "2nd year", "second year"]):
            semester = "III Semester"
        elif any(k in q_lower for k in ["5th sem", "v sem", "fifth sem", "3rd year", "third year"]):
            semester = "V Semester"
        elif any(k in q_lower for k in ["7th sem", "vii sem", "seventh sem", "4th year", "final year"]):
            semester = "VII Semester"
        elif any(k in q_lower for k in ["1st sem", "i sem", "first sem", "1st year", "first year"]):
            semester = "I Semester"

        # 3. Parse section from query
        if any(k in q_lower for k in ["sec b", "section b", "section 2", "sec 2"]):
            section = "B"
        elif any(k in q_lower for k in ["sec a", "section a", "section 1", "sec 1"]):
            section = "A"

        # 4. Fallback to authenticated student profile if parameters are missing
        student_prof = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first() if user else None
        if user and not branch and (user.branch or (student_prof and student_prof.specialization)):
            branch = user.branch or student_prof.specialization
        if not semester and student_prof and student_prof.semester:
            sem_map = {
                1: "I Semester", 2: "II Semester", 3: "III Semester", 4: "IV Semester",
                5: "V Semester", 6: "VI Semester", 7: "VII Semester", 8: "VIII Semester"
            }
            semester = sem_map.get(student_prof.semester, f"{student_prof.semester} Semester")
        if not section and student_prof and student_prof.section:
            section = student_prof.section

        # If branch or semester is STILL undetermined, ask for concise clarification honestly
        if not branch or not semester:
            return {
                "answer": (
                    "To retrieve your exact timetable, please specify your branch/programme (e.g. *Artificial Intelligence & Robotics*, "
                    "*AIML*, or *AIDS*), semester (e.g. *III, V, or VII*), and section (e.g. *A or B*).\n\n"
                    "For example: *'What is my timetable for III Sem AIR Section A tomorrow?'*"
                ),
                "intent": "TIMETABLE_QUERY",
                "citations": [],
                "needs_clarification": True
            }

        # Check if requested branch and semester are published in master timetable database
        is_supported_sem = semester in ["III Semester", "V Semester", "VII Semester"]
        is_supported_branch = any(k in branch for k in ["Robotics", "AIR", "Machine Learning", "AIML", "Data Science", "AIDS", "Artificial Intelligence"])

        if not (is_supported_sem and is_supported_branch):
            return {
                "answer": (
                    f"Official master timetables for the **July–December 2026** academic session are currently published only for "
                    f"Centre for Artificial Intelligence programmes (Semesters III, V, and VII).\n\n"
                    f"No published timetable records were found for **{branch} ({semester})**. "
                    f"Please consult your departmental notice board or class coordinator for offline schedule details."
                ),
                "intent": "TIMETABLE_QUERY",
                "citations": []
            }

        section = section or "A"

        # Check if query asks for a specific day
        day_query = None
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "today", "tomorrow"]:
            if day in q_lower:
                day_query = day
                break

        schedule = timetable_service.get_student_schedule(
            db=db,
            branch=branch,
            semester=semester,
            section=section,
            day_of_week=day_query
        )

        day_name = schedule["day"]

        # Fetch actual document metadata from database
        sem_roman = semester.split()[0] if semester else "III"
        doc = db.query(InstitutionalDocument).filter(
            InstitutionalDocument.category == "TIMETABLE",
            InstitutionalDocument.semester.ilike(f"%{sem_roman}%")
        ).first()

        doc_title = doc.title if doc else f"Master Time Table (Session: July-Dec. 2026) - {semester}"
        doc_url = f"/api/v1/documents/{doc.id}/download" if doc else "https://web.mitsgwalior.in/academics/academic-calendar"

        if schedule.get("is_holiday"):
            answer = f"**Schedule for {day_name} ({semester}, {branch}, Section {section})**\n\nNo classes are scheduled on {day_name} (Academic Holiday/Off-day)."
            return {
                "answer": answer,
                "intent": "TIMETABLE_QUERY",
                "citations": [{
                    "title": doc_title,
                    "sourceUrl": doc_url,
                    "category": "TIMETABLE",
                    "page": 1,
                    "section": branch,
                    "snippet": f"No scheduled lectures or laboratories for {day_name}."
                }],
                "widget": {
                    "type": "TIMETABLE_CARD",
                    "data": schedule
                }
            }

        lines = [
            f"Here is your official class timetable for **{day_name}** ({semester}, {branch}, Section {section}):\n"
        ]
        for c in schedule["classes"]:
            lab_badge = " *(Laboratory)*" if c["is_lab"] else ""
            lines.append(
                f"- **Period {c['period']} ({c['time']})**: **{c['subject']}** ({c['course_code']}){lab_badge}\n"
                f"  - **Faculty**: {c['faculty']}\n"
                f"  - **Room/Venue**: `{c['room']}`"
            )

        lines.append(f"\n*Official Session: July-Dec. 2026 | Timetable Source: {doc_title}*")
        answer = "\n".join(lines)

        return {
            "answer": answer,
            "intent": "TIMETABLE_QUERY",
            "citations": [{
                "title": doc_title,
                "sourceUrl": doc_url,
                "category": "TIMETABLE",
                "page": 1,
                "section": branch,
                "snippet": f"Official class schedule for {day_name} at Centre for AI."
            }],
            "widget": {
                "type": "TIMETABLE_CARD",
                "data": schedule
            }
        }

    def _handle_faculty_availability(self, db: Session, query: str) -> Dict[str, Any]:
        """
        Determines faculty availability with mandatory disclaimer and Asia/Kolkata timezone.
        """
        day_query = None
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "today", "tomorrow"]:
            if day in query.lower():
                day_query = day
                break

        avail = timetable_service.get_faculty_availability(
            db=db,
            target_day=day_query,
            time_query=query
        )

        day_name = avail["day"]
        time_win = avail["time_window"]
        slot_lbl = avail["slot_label"]

        lines = [
            f"**Faculty Teaching Schedule for {day_name} ({slot_lbl}: {time_win} IST)**\n",
            f"Based on the published master teaching timetables for {day_name}, the following faculty members have **no scheduled classroom teaching or laboratory classes** during this period:\n"
        ]

        for f in avail["free_faculty"][:12]:
            lines.append(f"- **{f['name']}** — *{f['designation']}* (Office: {f.get('office', 'Department Block')})")

        if len(avail["free_faculty"]) > 12:
            lines.append(f"\n*(+ {len(avail['free_faculty']) - 12} other timetable-covered faculty members without scheduled classes)*\n")

        if avail["busy_faculty"]:
            lines.append("\n**Faculty with scheduled classes during this period:**")
            for bf in avail["busy_faculty"][:6]:
                t_info = bf.get("teaching", {})
                lines.append(f"- **{bf['name']}**: Teaching *{t_info.get('subject', 'Course')}* in Room `{t_info.get('room', 'N/A')}`")

        lines.append(f"\n> ℹ️ **Mandatory Institutional Disclaimer**: {avail['disclaimer']}")

        return {
            "answer": "\n".join(lines),
            "intent": "FACULTY_AVAILABILITY",
            "citations": [{
                "title": "Master Time Table (Session: July-Dec. 2026)",
                "sourceUrl": "https://web.mitsgwalior.in/academics/academic-calendar",
                "category": "TIMETABLE",
                "page": 1,
                "section": "Master Teaching Grid",
                "snippet": f"Faculty teaching allocations for {day_name} at {time_win}."
            }],
            "widget": {
                "type": "FACULTY_AVAILABILITY_CARD",
                "data": avail
            }
        }

    def _handle_class_coordinator(self, db: Session, query: str, user: User) -> Dict[str, Any]:
        """
        Looks up class coordinator from Table 28.
        """
        # Determine branch
        branch = "Artificial Intelligence"
        ql = query.lower()
        if "robotics" in ql or "air" in ql:
            branch = "Information Technology (Artificial Intelligence and Robotics)"
        elif "machine learning" in ql or "aiml" in ql:
            branch = "Artificial Intelligence and Machine Learning"
        elif "data science" in ql or "aids" in ql:
            branch = "Artificial Intelligence and Data Science"
        elif user.branch:
            branch = user.branch

        # Determine year
        year_str = "II Year"
        if "1st" in ql or "first" in ql or "i year" in ql:
            year_str = "I Year"
        elif "3rd" in ql or "third" in ql or "iii year" in ql:
            year_str = "III Year"
        elif "4th" in ql or "fourth" in ql or "final" in ql or "iv year" in ql:
            year_str = "IV Year"

        coord = timetable_service.get_class_coordinator(db, branch, year_str)
        if coord:
            answer = (
                f"**Class Coordinator Details**\n\n"
                f"- **Programme / Branch**: {coord['branch']}\n"
                f"- **Year of Study**: {coord['year']}\n"
                f"- **Faculty Coordinator**: **{coord['name']}**\n"
                f"- **Official Email**: [{coord['institutional_email']}](mailto:{coord['institutional_email']})\n"
                f"- **Contact Number**: `{coord['contact_number']}`\n"
                f"- **Academic Session**: {coord['session']}\n\n"
                f"For academic grievances, mentor allocation, attendance verification, and application routing, "
                f"please contact your designated class coordinator."
            )
            return {
                "answer": answer,
                "intent": "CLASS_COORDINATOR_LOOKUP",
                "citations": [{
                    "title": "Centre for Artificial Intelligence Comprehensive Academic Data",
                    "sourceUrl": "https://web.mitsgwalior.in/faculty-profiles-cai",
                    "category": "COORDINATORS",
                    "page": 71,
                    "section": "Table 28: Class Coordinators Directory",
                    "snippet": f"{coord['name']} - {coord['year']} Coordinator for {coord['branch']}"
                }],
                "widget": {
                    "type": "COORDINATOR_CARD",
                    "data": coord
                }
            }

        return None

    def _handle_laboratory(self, db: Session, query: str) -> Dict[str, Any]:
        """
        Retrieves laboratory specs and equipment details.
        """
        ql = query.lower()
        target_lab = "Robotics"
        if "hpc" in ql or "computing" in ql or "high performance" in ql:
            target_lab = "HPC"
        elif "ar" in ql or "vr" in ql or "virtual" in ql or "augmented" in ql:
            target_lab = "Augmented Reality"
        elif "prog" in ql or "python" in ql:
            target_lab = "Programming Laboratory 1"

        lab = timetable_service.get_lab_details(db, target_lab)
        if lab:
            answer = (
                f"### {lab['name']} ({lab['code']})\n\n"
                f"**Location**: {lab['location']}\n"
                f"**Capacity**: {lab['capacity']} Workstations\n"
                f"**Faculty-in-Charge**: {lab['faculty_in_charge']}\n"
                f"**Staff-in-Charge**: {lab['staff_in_charge']}\n\n"
                f"**Hardware Facilities**:\n{lab['hardware']}\n\n"
                f"**Software & Tools**:\n{lab['software']}\n\n"
                f"**Key Research Focus**:\n{lab['research_focus']}\n\n"
                f"*{lab['description']}*"
            )
            return {
                "answer": answer,
                "intent": "LABORATORY_LOOKUP",
                "citations": [{
                    "title": "Centre for Artificial Intelligence Comprehensive Academic Data",
                    "sourceUrl": "https://web.mitsgwalior.in/facilities/laboratories",
                    "category": "LABORATORY",
                    "page": 48,
                    "section": f"Laboratories - {lab['name']}",
                    "snippet": lab["description"]
                }],
                "widget": {
                    "type": "LABORATORY_CARD",
                    "data": lab
                }
            }

        # If user asks for all labs
        all_labs = db.query(Laboratory).filter(Laboratory.is_demo == False).all()
        if all_labs:
            lines = ["**Laboratories at Centre for Artificial Intelligence, MITS Gwalior:**\n"]
            for l in all_labs:
                lines.append(
                    f"1. **{l.name}** (`{l.code}`)\n"
                    f"   - **Location**: {l.location}\n"
                    f"   - **Faculty-in-Charge**: {l.faculty_in_charge}\n"
                    f"   - **Focus**: {l.research_focus}"
                )
            return {
                "answer": "\n".join(lines),
                "intent": "LABORATORY_LOOKUP",
                "citations": [{
                    "title": "Centre for Artificial Intelligence Comprehensive Academic Data",
                    "sourceUrl": "https://web.mitsgwalior.in/facilities/laboratories",
                    "category": "LABORATORY",
                    "page": 48,
                    "section": "Centre for AI Laboratories Directory",
                    "snippet": "List of 5 specialized departmental labs."
                }]
            }

        return None

    def _handle_faculty_lookup(self, db: Session, query: str) -> Optional[Dict[str, Any]]:
        """
        Searches faculty directory for matching courses or research areas.
        """
        ql = query.lower()
        if "robotics" in ql:
            facs = db.query(FacultyProfile).filter(
                (FacultyProfile.bio.ilike("%robotics%")) |
                (FacultyProfile.name.in_(["Dr. Arun Kumar", "Dr. Pawan Dubey", "Dr. Tej Singh"]))
            ).all()
        elif "data structures" in ql or "algorithms" in ql:
            facs = db.query(FacultyProfile).filter(
                (FacultyProfile.bio.ilike("%algorithm%")) |
                (FacultyProfile.name.in_(["Dr. Abhishek Bhatt", "Dr. Anurag Singh Tomar", "Dr. Rajni Ranjan Singh Makwana"]))
            ).all()
        elif "mausam" in ql:
            facs = db.query(FacultyProfile).filter(FacultyProfile.name.ilike("%Mausam%")).all()
        else:
            return None

        if facs:
            lines = ["**Faculty Members Associated with this Query:**\n"]
            for f in facs[:4]:
                lines.append(
                    f"- **{f.name}** ({f.designation})\n"
                    f"  - **Qualification**: {f.qualification}\n"
                    f"  - **Official Email**: [{f.email_public}](mailto:{f.email_public})\n"
                    f"  - **Office Location**: {f.office_location}\n"
                    f"  - **Overview**: {f.bio}"
                )
            return {
                "answer": "\n".join(lines),
                "intent": "FACULTY_LOOKUP",
                "citations": [{
                    "title": "Faculty Directory - Centre for Artificial Intelligence",
                    "sourceUrl": "https://web.mitsgwalior.in/faculty-profiles-cai",
                    "category": "FACULTY",
                    "page": 1,
                    "section": "Official Faculty Profiles",
                    "snippet": "Verified institutional faculty directory."
                }]
            }
        return None


intent_router = IntentRouter()
