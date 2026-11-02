import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import zoneinfo
from sqlalchemy.orm import Session
from backend.app.models.academic_records import TimetableEntry
from backend.app.models.faculty import FacultyProfile
from backend.app.models.academic import ClassCoordinator, Laboratory
from backend.app.models.identity import User

logger = logging.getLogger("pocketuni.timetable")

# Authoritative time slot standards for MITS Master Timetables (Session: July-Dec 2026)
# Verified directly against official scanned timetable PDFs (III, V, VII Semesters)
SLOT_TIMINGS = {
    0: ("09:00 AM", "10:00 AM", "Slot 0 / Morning"),
    1: ("10:00 AM", "11:00 AM", "Period 1"),
    2: ("11:00 AM", "12:00 PM", "Period 2"),
    3: ("12:00 PM", "01:00 PM", "Period 3"),
    4: ("02:00 PM", "03:00 PM", "Period 4"),
    5: ("03:00 PM", "04:00 PM", "Period 5"),
    6: ("04:00 PM", "05:00 PM", "Period 6"),
    7: ("05:00 PM", "06:00 PM", "Slot 7 / Extended Lab"),
}

FACULTY_CODE_MAP = {
    "RRS": "Dr. Rajni Ranjan Singh Makwana",
    "AS": "Dr. Anu Sayal",
    "MSA": "Dr. Mir Shahnawaz Ahmad",
    "AK": "Dr. Arun Kumar",
    "TS": "Dr. Tej Singh",
    "VT": "Dr. Vibha Tiwari",
    "SKS": "Dr. Sunil Kumar Shukla",
    "SD": "Dr. Sumit Dhariwal",
    "SM": "Dr. Shubha Mishra",
    "SS": "Dr. Shipra Shukla",
    "SO": "Dr. Satyam Omar",
    "RKS": "Dr. Rahul Kumar Sharma",
    "PD": "Dr. Pawan Dubey",
    "NM": "Dr. Neeraj Mishra",
    "NA": "Dr. Neelam Arya",
    "MC": "Dr. Mausam Chouksey",
    "HSP": "Dr. Hardev Singh Pal",
    "BSR": "Dr. Bhagat S. Raghuwanshi",
    "AST": "Dr. Anurag Singh Tomar",
    "AB": "Dr. Abhishek Bhatt",
    "VSS": "Dr. Vijay Shankar Sharma",
    "RDP": "Dr. Rishabh Deo Pandey",
    "NH": "Dr. Nidhi Humnekar",
    "PSK": "Dr. Pritha Singh Kushwah",
    "MS": "Dr. Mehuli Santra",
    "PT": "Ms. Pooja Tripathi",
    "AA": "Ms. Archana Acharya",
    "GH": "Mrs. Geetika Hazra",
    "RS": "Mr. Ramnaresh Sharma",
    "RST": "Mr. Rahul Senthiya",
}

# Authoritative Master Course Code to Name
COURSE_CATALOG = {
    # III Sem Courses
    "24252101": ("Probability and Statistics", "Theory", 4.0),
    "24252102": ("Design & Analysis of Algorithms", "Theory", 4.0),
    "24252103": ("Database Management System", "Theory", 4.0),
    "24252104": ("Discrete Mathematical Structures", "Theory", 3.0),
    "24252105": ("Operating Systems", "Theory", 4.0),
    "24252106": ("Python Programming Laboratory", "Practical", 1.5),
    "24252107": ("Design & Analysis of Algorithms Lab", "Practical", 1.5),
    "24252108": ("Data Science Laboratory", "Practical", 1.5),
    "24252109": ("Database Management Systems Lab", "Practical", 1.5),
    "24252110": ("Language Laboratory", "Practical", 1.0),
    "24252111": ("Cyber Security Foundations", "Theory", 2.0),
    "31252101": ("Probability and Statistics", "Theory", 4.0),
    "31252102": ("Design & Analysis of Algorithms", "Theory", 4.0),
    "31252103": ("Database Management System", "Theory", 4.0),
    "31252104": ("Digital Logic Design", "Theory", 3.0),
    "31252105": ("Operating Systems", "Theory", 4.0),
    "31252106": ("Algorithms Laboratory", "Practical", 1.5),
    "31252107": ("Operating Systems Laboratory", "Practical", 1.5),
    "31252108": ("Language Laboratory", "Practical", 1.0),
    "31252109": ("Database Management Systems Lab", "Practical", 1.5),
    "31252110": ("Creative Problem Solving", "Practical", 1.0),
    "31252111": ("Universal Human Values & Professional Ethics", "Theory", 2.0),
    "27252101": ("Probability and Statistics", "Theory", 4.0),
    "27252102": ("Design & Analysis of Algorithms", "Theory", 4.0),
    "27252103": ("Database Management System", "Theory", 4.0),
    "27252104": ("Computer Networks", "Theory", 4.0),
    "27252105": ("Operating Systems", "Theory", 4.0),
    "27252106": ("Python Programming Lab", "Practical", 1.5),
    "27252107": ("Design & Analysis of Algorithms Lab", "Practical", 1.5),
    "27252108": ("Semester Proficiency", "Practical", 1.0),
    "27252109": ("Macro Project-I", "Practical", 2.0),
    "27252110": ("Self-learning/Presentation", "Practical", 1.0),
    "27252111": ("Cyber Security", "Theory", 2.0),
    # V Sem Courses
    "24243101": ("Machine Learning", "Theory", 4.0),
    "24243102": ("Robot Kinematics and Dynamics", "Theory", 4.0),
    "24243103": ("Deep Learning", "Theory", 4.0),
    "24243104": ("Embedded AI Systems", "Theory", 3.0),
    "24243105": ("Robotics Laboratory", "Practical", 2.0),
    "24243106": ("Internet of Things Lab", "Practical", 2.0),
    "24243107": ("Professional Skills & Competencies", "Practical", 1.0),
    "24243108": ("HPC & Deep Learning Lab", "Practical", 2.0),
    "24243109": ("Cornerstone Project", "Practical", 3.0),
    "24243110": ("Supply Chain Management", "Theory", 3.0),
    "31243101": ("Machine Learning", "Theory", 4.0),
    "31243102": ("Deep Neural Networks", "Theory", 4.0),
    "31243103": ("Natural Language Processing", "Theory", 4.0),
    "31243104": ("Computer Vision", "Theory", 4.0),
    "31243105": ("Deep Learning Laboratory", "Practical", 2.0),
    "31243106": ("Natural Language Processing Lab", "Practical", 2.0),
    "31243107": ("Cloud Computing & Virtualization", "Theory", 3.0),
    "31243108": ("Computer Vision Laboratory", "Practical", 2.0),
    "31243109": ("AI Ethics and Governance", "Theory", 2.0),
    "31243110": ("Cornerstone Project", "Practical", 3.0),
    "27243101": ("Data Mining and Warehousing", "Theory", 4.0),
    "27243102": ("Cloud Computing & Virtualization", "Theory", 4.0),
    "27243103": ("Evolutionary Algorithms and Optimization", "Theory", 4.0),
    "27243104": ("Machine Learning", "Theory", 4.0),
    "27243105": ("Data Mining and Warehousing Lab", "Practical", 2.0),
    "27243106": ("Cloud Computing & Virtualization Lab", "Practical", 2.0),
    "27243107": ("Semester Proficiency", "Practical", 1.0),
    "27243108": ("Machine Learning Lab", "Practical", 2.0),
    "27243109": ("Cornerstone Project", "Practical", 3.0),
    "27243110": ("Supply Chain Management", "Theory", 3.0),
    "28243101": ("Machine Learning Foundations", "Theory", 4.0),
    "28243102": ("Deep Learning Architectures", "Theory", 4.0),
    "28243103": ("Pattern Recognition", "Theory", 4.0),
    "28243104": ("Reinforcement Learning", "Theory", 4.0),
    "28243105": ("Machine Learning Studio Lab", "Practical", 2.0),
    "28243106": ("Deep Learning Studio Lab", "Practical", 2.0),
    "28243107": ("Cloud AI & MLOps", "Theory", 3.0),
    "28243108": ("Reinforcement Learning Lab", "Practical", 2.0),
    "28243109": ("Cornerstone Project", "Practical", 3.0),
    "28243110": ("Cognitive Computing", "Theory", 3.0),
    # VII Sem Courses
    "24234101": ("Autonomous Navigation & ROS", "Theory", 4.0),
    "24234102": ("Swarm Robotics", "Theory", 4.0),
    "24234103": ("Human-Robot Interaction", "Theory", 4.0),
    "24234104": ("Major Project-I", "Practical", 6.0),
    "31234101": ("Generative AI & LLMs", "Theory", 4.0),
    "31234102": ("Reinforcement Learning & Multi-Agent Systems", "Theory", 4.0),
    "31234103": ("Major Project-I", "Practical", 6.0),
}


class TimetableService:
    """
    Core timetable intelligence and resolver service.
    Translates raw timetable grids into personalized schedule queries,
    faculty availability queries, and class coordinator lookups.
    """

    def __init__(self):
        self.tz = zoneinfo.ZoneInfo("Asia/Kolkata")

    def seed_master_timetables(self, db: Session) -> int:
        """
        Seeds official master timetables parsed from July-Dec 2026 session documents.
        """
        existing = db.query(TimetableEntry).count()
        if existing >= 50:
            logger.info(f"Timetable entries already present: {existing}")
            return existing

        entries_to_insert = []

        # Master schedules defined per branch, semester, section, and day
        # Format: (branch, semester, section, day, slot_no, course_code, faculty_code, room, is_lab)
        schedules = [
            # -------------------------------------------------------------------------
            # B.Tech IT (AI & Robotics) - III Semester
            # -------------------------------------------------------------------------
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Tuesday", 1, "24252105", "RRS", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Tuesday", 2, "24252101", "VSS", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Tuesday", 3, "24252102", "AST", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Tuesday", 4, "24252110", "RS", "Language Lab", 1),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Tuesday", 5, "24252108", "MS", "Programming Lab 1", 1),

            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Wednesday", 1, "24252105", "RRS", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Wednesday", 2, "24252102", "AST", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Wednesday", 3, "24252101", "VSS", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Wednesday", 4, "24252111", "PT", "M201", 0),

            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Thursday", 1, "24252103", "NM", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Thursday", 2, "24252102", "AST", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Thursday", 3, "24252105", "RRS", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Thursday", 4, "24252107", "AST", "M203", 1),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Thursday", 5, "24252104", "SD", "M201", 0),

            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Friday", 1, "24252101", "VSS", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Friday", 2, "24252103", "NM", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Friday", 3, "24252104", "SD", "M201", 0),

            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Saturday", 1, "24252103", "NM", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Saturday", 2, "24252101", "VSS", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Saturday", 3, "24252104", "SD", "M201", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Saturday", 4, "24252106", "AST", "Programming Lab 2", 1),
            ("Information Technology (Artificial Intelligence and Robotics)", "III Semester", "A", "Saturday", 5, "24252109", "RS", "M104", 1),

            # -------------------------------------------------------------------------
            # B.Tech Artificial Intelligence - III Semester (Section 1)
            # -------------------------------------------------------------------------
            ("Artificial Intelligence", "III Semester", "1", "Tuesday", 1, "31252105", "RS", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Tuesday", 2, "31252102", "SS", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Tuesday", 3, "31252104", "SD", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Tuesday", 4, "31252101", "SO", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Tuesday", 5, "31252103", "BSR", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Tuesday", 6, "31252109", "BSR", "Programming Lab 2", 1),

            ("Artificial Intelligence", "III Semester", "1", "Wednesday", 1, "31252101", "SO", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Wednesday", 2, "31252104", "SD", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Wednesday", 3, "31252110", "GH", "M202", 0),

            ("Artificial Intelligence", "III Semester", "1", "Thursday", 1, "31252101", "SO", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Thursday", 2, "31252102", "SS", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Thursday", 3, "31252103", "BSR", "M202", 0),

            ("Artificial Intelligence", "III Semester", "1", "Friday", 1, "31252102", "SS", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Friday", 2, "31252105", "RS", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Friday", 3, "31252101", "SO", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Friday", 4, "31252104", "SD", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Friday", 5, "31252107", "SS", "M203", 1),

            ("Artificial Intelligence", "III Semester", "1", "Saturday", 1, "31252108", "NH", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Saturday", 2, "31252105", "RS", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Saturday", 3, "31252103", "BSR", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Saturday", 4, "31252111", "GH", "M202", 0),
            ("Artificial Intelligence", "III Semester", "1", "Saturday", 5, "31252106", "RDP", "Programming Lab 1", 1),

            # -------------------------------------------------------------------------
            # B.Tech AI & Data Science - III Semester
            # -------------------------------------------------------------------------
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Tuesday", 1, "27252111", "PT", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Tuesday", 2, "27252105", "RS", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Tuesday", 4, "27252104", "PT", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Tuesday", 5, "27252101", "SO", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Tuesday", 6, "27252106", "PD", "Programming Lab 1", 1),

            ("Artificial Intelligence and Data Science", "III Semester", "A", "Wednesday", 1, "27252102", "HSP", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Wednesday", 2, "27252103", "AK", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Wednesday", 3, "27252105", "RS", "SH1", 0),

            ("Artificial Intelligence and Data Science", "III Semester", "A", "Thursday", 1, "27252102", "HSP", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Thursday", 2, "27252101", "SO", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Thursday", 3, "27252104", "PT", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Thursday", 4, "27252107", "HSP", "Programming Lab 2", 1),

            ("Artificial Intelligence and Data Science", "III Semester", "A", "Friday", 1, "27252103", "AK", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Friday", 2, "27252101", "SO", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Friday", 3, "27252105", "RS", "SH1", 0),

            ("Artificial Intelligence and Data Science", "III Semester", "A", "Saturday", 1, "27252103", "AK", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Saturday", 2, "27252102", "HSP", "SH1", 0),
            ("Artificial Intelligence and Data Science", "III Semester", "A", "Saturday", 3, "27252104", "PT", "SH1", 0),

            # -------------------------------------------------------------------------
            # B.Tech IT (AI & Robotics) - V Semester
            # -------------------------------------------------------------------------
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Tuesday", 1, "24243109", "PD", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Tuesday", 2, "24243101", "BSR", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Wednesday", 1, "24243104", "SKS", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Wednesday", 2, "24243102", "NM", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Wednesday", 3, "24243103", "PD", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Thursday", 1, "24243110", "VSS", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Thursday", 2, "24243102", "NM", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Thursday", 3, "24243103", "PD", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Thursday", 4, "24243104", "SKS", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Thursday", 5, "24243105", "PD", "Robotics Laboratory", 1),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Friday", 1, "24243101", "BSR", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Friday", 2, "24243102", "NM", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Friday", 3, "24243103", "PD", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Friday", 4, "24243104", "SKS", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Saturday", 1, "24243106", "NM", "Robotics Laboratory", 1),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Saturday", 2, "24243101", "BSR", "J110", 0),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Saturday", 3, "24243108", "SKS", "HPC Laboratory", 1),
            ("Information Technology (Artificial Intelligence and Robotics)", "V Semester", "A", "Saturday", 4, "24243107", "PT", "J110", 0),

            # -------------------------------------------------------------------------
            # B.Tech AI & Machine Learning - V Semester
            # -------------------------------------------------------------------------
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Tuesday", 1, "28243105", "MC", "Programming Lab 1", 1),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Tuesday", 4, "28243101", "MC", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Tuesday", 5, "28243104", "TS", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Tuesday", 6, "28243102", "AA", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Wednesday", 1, "28243105", "MC", "Programming Lab 2", 1),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Wednesday", 2, "28243104", "TS", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Wednesday", 4, "28243101", "MC", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Wednesday", 5, "28243107", "AA", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Thursday", 1, "28243106", "TS", "Programming Lab 1", 1),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Thursday", 2, "28243103", "HSP", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Thursday", 4, "28243101", "MC", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Thursday", 5, "28243110", "NH", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Friday", 1, "28243103", "HSP", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Friday", 2, "28243104", "TS", "J109", 0),
            ("Artificial Intelligence and Machine Learning", "V Semester", "A", "Friday", 3, "28243109", "VT", "J109", 0),
        ]

        for branch, sem, sec, day, slot_no, code, fac_code, room, is_lab in schedules:
            start_t, end_t, slot_lbl = SLOT_TIMINGS[slot_no]
            sub_name, sub_type, credits = COURSE_CATALOG.get(code, (f"Course {code}", "Theory", 4.0))
            fac_name = FACULTY_CODE_MAP.get(fac_code, f"Faculty {fac_code}")

            entry = TimetableEntry(
                day=day,
                start_time=start_t,
                end_time=end_t,
                slot_number=slot_no,
                subject=sub_name,
                subject_code=code,
                faculty_name=fac_name,
                room=room,
                programme="B.Tech",
                branch=branch,
                semester=sem,
                section=sec,
                batch_group="All",
                is_lab=is_lab,
                academic_year="2026-2027",
                effective_period="July-Dec 2026",
                is_demo=False,
            )
            entries_to_insert.append(entry)

        db.bulk_save_objects(entries_to_insert)
        db.commit()
        logger.info(f"Seeded {len(entries_to_insert)} master timetable entries.")
        return len(entries_to_insert)

    def get_current_ist_time(self) -> datetime:
        return datetime.now(self.tz)

    def resolve_day_of_week(self, day_query: Optional[str] = None, target_date: Optional[date] = None) -> str:
        """
        Resolves day of week in Asia/Kolkata timezone:
        'today', 'tomorrow', 'Monday', None -> returns capitalized day name.
        """
        now = self.get_current_ist_time()
        if target_date:
            return target_date.strftime("%A")

        if not day_query:
            return now.strftime("%A")

        dq = day_query.strip().lower()
        if dq in ["today", "aaj"]:
            return now.strftime("%A")
        elif dq in ["tomorrow", "kal"]:
            return (now + timedelta(days=1)).strftime("%A")
        elif dq in ["yesterday"]:
            return (now - timedelta(days=1)).strftime("%A")

        days_map = {
            "mon": "Monday", "monday": "Monday",
            "tue": "Tuesday", "tuesday": "Tuesday",
            "wed": "Wednesday", "wednesday": "Wednesday",
            "thu": "Thursday", "thursday": "Thursday",
            "fri": "Friday", "friday": "Friday",
            "sat": "Saturday", "saturday": "Saturday",
            "sun": "Sunday", "sunday": "Sunday"
        }
        for k, v in days_map.items():
            if k in dq:
                return v

        return now.strftime("%A")

    def get_student_schedule(
        self,
        db: Session,
        branch: str,
        semester: str,
        section: str = "A",
        day_of_week: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Retrieves the exact personalized class schedule for a student.
        """
        resolved_day = self.resolve_day_of_week(day_of_week, target_date)
        if resolved_day == "Sunday":
            return {
                "day": "Sunday",
                "is_holiday": True,
                "class_count": 0,
                "message": "Sunday is an academic holiday. No scheduled classes or laboratories.",
                "classes": []
            }

        # Normalize branch matching
        q = db.query(TimetableEntry).filter(
            TimetableEntry.day == resolved_day,
            TimetableEntry.semester.ilike(f"%{semester.replace('Semester', '').strip()}%")
        )

        if "Robotics" in branch or "AIR" in branch:
            q = q.filter(TimetableEntry.branch.ilike("%Robotics%"))
        elif "Machine Learning" in branch or "AIML" in branch:
            q = q.filter(TimetableEntry.branch.ilike("%Machine Learning%"))
        elif "Data Science" in branch or "AIDS" in branch:
            q = q.filter(TimetableEntry.branch.ilike("%Data Science%"))
        elif "Artificial Intelligence" in branch or "AI" in branch:
            q = q.filter(TimetableEntry.branch == "Artificial Intelligence")

        entries = q.order_by(TimetableEntry.slot_number.asc()).all()

        classes = []
        for e in entries:
            classes.append({
                "period": e.slot_number,
                "time": f"{e.start_time} - {e.end_time}",
                "course_code": e.subject_code,
                "subject": e.subject,
                "faculty": e.faculty_name,
                "room": e.room,
                "is_lab": bool(e.is_lab),
            })

        return {
            "day": resolved_day,
            "branch": branch,
            "semester": semester,
            "section": section,
            "is_holiday": len(classes) == 0,
            "class_count": len(classes),
            "classes": classes,
            "effective_session": "July-Dec 2026",
            "timezone": "Asia/Kolkata",
        }

    def get_faculty_availability(
        self,
        db: Session,
        target_day: Optional[str] = None,
        slot_number: Optional[int] = None,
        time_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Determines faculty availability for a given time slot based on published master timetables.
        Includes mandatory non-confirmation disclaimer with Asia/Kolkata timezone.
        """
        resolved_day = self.resolve_day_of_week(target_day)

        # Map 2 PM, 14:00, 10 AM, etc. to slot numbers if not provided
        if slot_number is None and time_query:
            tq = time_query.lower()
            if "9 am" in tq or "09:00" in tq or "9:00" in tq:
                slot_number = 0
            elif "10:00" in tq or "10 am" in tq:
                slot_number = 1
            elif "11:00" in tq or "11 am" in tq:
                slot_number = 2
            elif "12:00" in tq or "12 pm" in tq:
                slot_number = 3
            elif "1:00" in tq or "1 pm" in tq or "13:00" in tq:
                slot_number = 4  # Post-lunch Period 4
            elif "2:00" in tq or "2 pm" in tq or "14:00" in tq:
                slot_number = 4
            elif "3:00" in tq or "3 pm" in tq or "15:00" in tq:
                slot_number = 5
            elif "4:00" in tq or "4 pm" in tq or "16:00" in tq:
                slot_number = 6
            elif "5:00" in tq or "5 pm" in tq or "17:00" in tq:
                slot_number = 7
            else:
                slot_number = 4  # Default to Period 4 (02:00 - 03:00 PM)

        slot_number = 4 if slot_number is None else slot_number
        start_t, end_t, slot_lbl = SLOT_TIMINGS.get(slot_number, ("02:00 PM", "03:00 PM", "Period 4"))

        # 1. Identify all faculty members who have known timetable coverage in published schedules
        all_tt_faculty_records = db.query(TimetableEntry.faculty_name).distinct().all()
        known_tt_faculty_names = set(r[0] for r in all_tt_faculty_records if r and r[0])

        # 2. Find busy faculty in this slot
        busy_entries = db.query(TimetableEntry).filter(
            TimetableEntry.day == resolved_day,
            TimetableEntry.slot_number == slot_number
        ).all()

        busy_faculty_names = set(e.faculty_name for e in busy_entries if e.faculty_name)

        # 3. Query all non-demo faculty
        all_faculty = db.query(FacultyProfile).filter(FacultyProfile.is_demo == False).all()

        free_faculty = []
        busy_faculty = []
        unknown_coverage_faculty = []

        for f in all_faculty:
            # Check if faculty has known timetable coverage
            has_coverage = any(
                f.name.lower() in kf.lower() or kf.lower() in f.name.lower()
                for kf in known_tt_faculty_names
            )

            if not has_coverage:
                unknown_coverage_faculty.append({
                    "name": f.name,
                    "designation": f.designation,
                    "department": f.department,
                    "status": "Schedule not covered in currently published master timetables."
                })
                continue

            # Check if busy in this slot
            is_busy = any(f.name.lower() in bf.lower() or bf.lower() in f.name.lower() for bf in busy_faculty_names)
            item = {
                "name": f.name,
                "designation": f.designation,
                "email": f.email_public,
                "office": f.office_location,
            }
            if is_busy:
                entry = next((e for e in busy_entries if f.name.lower() in e.faculty_name.lower()), None)
                if entry:
                    item["teaching"] = {
                        "subject": entry.subject,
                        "room": entry.room,
                        "branch": entry.branch,
                        "semester": entry.semester,
                    }
                busy_faculty.append(item)
            else:
                item["status"] = "According to the published timetable, no class is listed for this faculty member during this period."
                free_faculty.append(item)

        ist_now = self.get_current_ist_time().strftime("%Y-%m-%d %H:%M:%S IST")

        return {
            "day": resolved_day,
            "slot": slot_number,
            "time_window": f"{start_t} - {end_t}",
            "slot_label": slot_lbl,
            "free_faculty_count": len(free_faculty),
            "busy_faculty_count": len(busy_faculty),
            "unknown_coverage_count": len(unknown_coverage_faculty),
            "free_faculty": free_faculty,
            "busy_faculty": busy_faculty,
            "unknown_coverage_faculty": unknown_coverage_faculty,
            "timezone": "Asia/Kolkata",
            "query_timestamp": ist_now,
            "disclaimer": (
                "Note: Faculty availability is derived strictly from published master teaching timetables (Asia/Kolkata). "
                "Faculty without scheduled classes may still be engaged in departmental meetings, research, "
                "administrative duties, examination coordination, laboratory guidance, or student mentoring. "
                "Timetable data indicates no scheduled class, but unscheduled departmental duties or leave cannot be confirmed."
            )
        }

    def get_class_coordinator(self, db: Session, branch: str, semester_or_year: str) -> Optional[Dict[str, Any]]:
        """
        Returns class coordinator contact info from Table 28.
        """
        # Map semester to year label
        year_str = "I Year"
        sem_l = semester_or_year.lower()
        if "3" in sem_l or "4" in sem_l or "ii" in sem_l or "second" in sem_l or "3rd" in sem_l:
            year_str = "II Year"
        elif "5" in sem_l or "6" in sem_l or "iii" in sem_l or "third" in sem_l or "5th" in sem_l:
            year_str = "III Year"
        elif "7" in sem_l or "8" in sem_l or "iv" in sem_l or "fourth" in sem_l or "final" in sem_l or "7th" in sem_l:
            year_str = "IV Year"

        q = db.query(ClassCoordinator).filter(ClassCoordinator.year == year_str)
        if "Robotics" in branch or "AIR" in branch:
            q = q.filter(ClassCoordinator.branch.ilike("%Robotics%"))
        elif "Machine Learning" in branch or "AIML" in branch:
            q = q.filter(ClassCoordinator.branch.ilike("%Machine Learning%"))
        elif "Data Science" in branch or "AIDS" in branch:
            q = q.filter(ClassCoordinator.branch.ilike("%Data Science%"))
        else:
            q = q.filter(ClassCoordinator.branch == "Artificial Intelligence")

        coord = q.first()
        if coord:
            return {
                "name": coord.faculty_name,
                "branch": coord.branch,
                "year": coord.year,
                "contact_number": coord.contact_number,
                "institutional_email": coord.institutional_email,
                "session": coord.academic_session,
            }
        return None

    def get_lab_details(self, db: Session, lab_name_or_keyword: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed specs, hardware, software, and coordinators for a CAI laboratory.
        """
        kw = f"%{lab_name_or_keyword.strip()}%"
        lab = db.query(Laboratory).filter(
            (Laboratory.name.ilike(kw)) | (Laboratory.code.ilike(kw)) | (Laboratory.research_focus.ilike(kw))
        ).first()

        if lab:
            return {
                "name": lab.name,
                "code": lab.code,
                "location": lab.location,
                "capacity": lab.capacity,
                "hardware": lab.hardware_specs,
                "software": lab.software_specs,
                "faculty_in_charge": lab.faculty_in_charge,
                "staff_in_charge": lab.staff_in_charge,
                "research_focus": lab.research_focus,
                "description": lab.description,
            }
        return None


timetable_service = TimetableService()
