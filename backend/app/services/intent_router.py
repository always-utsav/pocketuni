import logging
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.identity import User
from backend.app.models.student import StudentProfile
from backend.app.models.faculty import FacultyProfile, FacultyResearchInterest
from backend.app.models.academic import Laboratory, ClassCoordinator
from backend.app.services.timetable_service import timetable_service
from backend.app.services.gemini_service import gemini_service

logger = logging.getLogger("pocketuni.intent_router")


class IntentRouter:
    """
    Deterministic academic intent classifier and specialized handler.
    Directs institutional inquiries to appropriate authoritative data resolvers.
    """

    def classify_intent(self, query: str) -> str:
        q = query.lower().strip()

        # 1. Faculty Availability
        if any(p in q for p in [
            "who is free", "is teacher free", "is faculty free", "available at",
            "no scheduled class", "free at", "teacher available", "faculty available",
            "teacher has no class", "free teacher", "free faculty"
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
        if intent == "TIMETABLE_QUERY":
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

    def _handle_timetable(self, db: Session, query: str, user: User) -> Dict[str, Any]:
        """
        Handles student timetable lookup grounded in authenticated profile context.
        """
        # Determine student branch and semester
        student_prof = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        branch = user.branch or (student_prof.specialization if student_prof else None) or "Information Technology (Artificial Intelligence and Robotics)"
        semester = f"{student_prof.semester} Semester" if student_prof and student_prof.semester else "III Semester"
        section = student_prof.section if student_prof and student_prof.section else "A"

        # Check if query asks for a specific day
        day_query = None
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "today", "tomorrow"]:
            if day in query.lower():
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
        if schedule.get("is_holiday"):
            answer = f"**Schedule for {day_name} ({semester}, {branch})**\n\nNo classes are scheduled on {day_name} (Academic Holiday/Off-day)."
            return {
                "answer": answer,
                "intent": "TIMETABLE_QUERY",
                "citations": [{
                    "title": f"Master Timetable (Session: July-Dec. 2026) - {semester}",
                    "sourceUrl": "https://web.mitsgwalior.in/academics/timetables",
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

        lines.append("\n*Official Session: July-Dec. 2026 (Centre for Artificial Intelligence)*")
        answer = "\n".join(lines)

        return {
            "answer": answer,
            "intent": "TIMETABLE_QUERY",
            "citations": [{
                "title": f"Master Time Table (Session: July-Dec. 2026) - {semester}",
                "sourceUrl": "https://web.mitsgwalior.in/academics/timetables",
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
            f"**Faculty Availability for {day_name} ({slot_lbl}: {time_win} IST)**\n",
            f"Based on the published teaching timetable for {day_name}, the following faculty members have **no scheduled classroom teaching or laboratory sessions** during this period:\n"
        ]

        for f in avail["free_faculty"][:12]:
            lines.append(f"- **{f['name']}** — *{f['designation']}* (Office: {f.get('office', 'Centre for AI')})")

        if len(avail["free_faculty"]) > 12:
            lines.append(f"\n*(+ {len(avail['free_faculty']) - 12} other department faculty members without scheduled classes)*\n")

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
                "sourceUrl": "https://web.mitsgwalior.in/academics/timetables",
                "category": "TIMETABLE",
                "page": 4,
                "section": "Faculty Workload Grid",
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
