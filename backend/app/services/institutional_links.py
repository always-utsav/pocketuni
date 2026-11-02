import re
from typing import Dict, Any, Optional, List

# Official verified institutional link registry for MITS-DU Gwalior
# Extracted from official institutional files, portals directory, and verified MITS web ecosystem
INSTITUTIONAL_LINK_REGISTRY: List[Dict[str, Any]] = [
    {
        "key": "student_ims",
        "title": "Integrated Management System (IMS) — Student Portal",
        "url": "https://ims.mitsgwalior.in/",
        "category": "STUDENT_SERVICES",
        "keywords": ["ims", "student ims", "fee receipt", "semester registration", "hostel allotment", "enrollment fee", "student login"],
        "description": "Student administrative portal for fee receipts, course registration, hostel allotment, and semester enrollment.",
        "department": "Dean Academics / Student Affairs",
        "source": "Official MITS E-Governance Registry",
        "verified": True
    },
    {
        "key": "faculty_mis",
        "title": "Management Information System (MIS) — Faculty & Staff Portal",
        "url": "http://mis.mitsgwalior.in/",
        "category": "ADMINISTRATIVE",
        "keywords": ["mis", "faculty mis", "staff portal", "faculty login", "leave application", "service book", "payroll"],
        "description": "Administrative human resources portal for faculty/staff leave applications, service book, and payroll records.",
        "department": "Establishment / HR",
        "source": "Official MITS E-Governance Registry",
        "verified": True
    },
    {
        "key": "moodle_lms",
        "title": "MITS Moodle Learning Management System",
        "url": "http://moodle.mitsgwalior.in/",
        "category": "LEARNING",
        "keywords": ["moodle", "lms", "courseware", "assignment upload", "lecture notes", "online quiz", "study material"],
        "description": "Online learning platform for course materials, quizzes, lab assignment submissions, and lecture notes.",
        "department": "Academic Computing Cell",
        "source": "Official MITS E-Governance Registry",
        "verified": True
    },
    {
        "key": "alumni_portal",
        "title": "MITS Global Alumni Network Portal",
        "url": "https://alumni.mitsgwalior.in/",
        "category": "ALUMNI",
        "keywords": ["alumni", "alumni portal", "alumni meet", "graduates network", "alumni registration"],
        "description": "Global alumni engagement directory facilitating mentorship, alumni meets, and institutional networking.",
        "department": "Alumni Relations Cell",
        "source": "Official MITS E-Governance Registry",
        "verified": True
    },
    {
        "key": "nec_registration",
        "title": "National Entrepreneurship Challenge (NEC) Portal",
        "url": "https://nec.mitsgwalior.in/",
        "category": "INNOVATION",
        "keywords": ["nec", "entrepreneurship", "startup", "incubation", "innovation challenge", "e-cell"],
        "description": "National Entrepreneurship Challenge registration and incubation tracking for student startups and innovation pitches.",
        "department": "Centre for Innovation & Entrepreneurship",
        "source": "Official MITS E-Governance Registry",
        "verified": True
    },
    {
        "key": "osm_evaluation",
        "title": "On-Screen Marking (OSM) — Answer Sheet Evaluation System",
        "url": "https://osm.mitsapps.in/ep_osm_web_landing",
        "category": "EXAMINATION",
        "keywords": ["osm", "answer sheet evaluation", "evaluation portal", "digital marking", "examiner login"],
        "description": "Digital answer script evaluation system used by authorized examiners to digitally mark semester exam booklets.",
        "department": "Controller of Examinations",
        "source": "Official Examination Portal Registry",
        "verified": True
    },
    {
        "key": "rrs_answersheet",
        "title": "Result & Answer Sheet Retrieval System (RRS)",
        "url": "https://rrs.mitsapps.in/ep_rds_web_landing",
        "category": "EXAMINATION",
        "keywords": ["rrs", "answer sheet download", "evaluated copy", "result copy", "revaluation", "grade card download"],
        "description": "Official portal for retrieving semester examination results and downloading evaluated digital answer sheets.",
        "department": "Controller of Examinations",
        "source": "Official Examination Portal Registry",
        "verified": True
    },
    {
        "key": "no_dues",
        "title": "MITS No Dues Clearance Portal",
        "url": "https://nbn.mitsgwalior.in",
        "category": "STUDENT_SERVICES",
        "keywords": ["no dues", "dues clearance", "library dues", "hostel dues", "clearance certificate", "caution money"],
        "description": "Online no-dues clearance portal for graduating students, library verification, and caution money refunds.",
        "department": "Dean Student Welfare",
        "source": "Official MITS Student Services",
        "verified": True
    },
    {
        "key": "elibrary_refread",
        "title": "MITS E-Library Portal (RefRead)",
        "url": "https://mits-rgpv.refread.com/#/home",
        "category": "LIBRARY",
        "keywords": ["e-library", "elibrary", "library", "digital library", "refread", "ieee explore", "springer books", "journals"],
        "description": "Remote institutional digital library offering off-campus access to IEEE Xplore, Springer, ScienceDirect, and e-books.",
        "department": "Central Library",
        "source": "Central Library Digital Access Registry",
        "verified": True
    },
    {
        "key": "irins_research",
        "title": "MITS Research Information Network (IRINS)",
        "url": "https://mitsgwalior.irins.org",
        "category": "RESEARCH",
        "keywords": ["irins", "research portal", "faculty publications", "citations", "h-index", "research profiles"],
        "description": "National Research Information Network profile of MITS Gwalior showcasing faculty publications, citations, and patents.",
        "department": "Dean R&D",
        "source": "INFLIBNET IRINS Registry",
        "verified": True
    },
    {
        "key": "mits_journal",
        "title": "MITS International Journal of Science & Technology",
        "url": "https://mitsjournal.mitsgwalior.in",
        "category": "RESEARCH",
        "keywords": ["journal", "mits journal", "paper submission", "manuscript", "peer reviewed journal"],
        "description": "Official peer-reviewed scientific journal of Madhav Institute of Technology & Science.",
        "department": "Editorial Board / Dean R&D",
        "source": "MITS Publications Office",
        "verified": True
    },
    {
        "key": "clc_admission",
        "title": "College Level Counselling (CLC) Admission Portal",
        "url": "http://clc.mitsweb.in:4242/",
        "category": "ADMISSIONS",
        "keywords": ["clc", "clc admission", "college level counselling", "spot admission", "direct admission", "vacant seats"],
        "description": "Official institutional portal for College Level Counselling (CLC) and spot admissions against vacant seats.",
        "department": "Admissions Cell",
        "source": "MITS Admissions Office",
        "verified": True
    },
    {
        "key": "dte_admission",
        "title": "DTE MP Online Admission Counselling Portal",
        "url": "https://dte.mponline.gov.in/",
        "category": "ADMISSIONS",
        "keywords": ["dte", "dte admission", "mp counselling", "jeemain counselling", "dte mponline"],
        "description": "Directorate of Technical Education (M.P.) centralized state counselling portal for B.Tech, M.Tech, and MCA admissions.",
        "department": "DTE Madhya Pradesh",
        "source": "State Technical Education Council",
        "verified": True
    },
    {
        "key": "academic_calendar",
        "title": "MITS Academic Calendar (Session 2026-27)",
        "url": "https://web.mitsgwalior.in/academics/academic-calendar",
        "category": "ACADEMICS",
        "keywords": ["academic calendar", "semester schedule", "exam dates", "holidays", "mst dates", "vacation dates"],
        "description": "Official academic calendar specifying semester commencement, MST schedules, fee deadlines, and semester-end examinations.",
        "department": "Dean Academics",
        "source": "web.mitsgwalior.in",
        "verified": True
    },
    {
        "key": "cai_department",
        "title": "Centre for Artificial Intelligence — Department Portal",
        "url": "https://web.mitsgwalior.in/academics/departments/centre-of-artificial-intelligence",
        "category": "DEPARTMENT",
        "keywords": ["cai", "centre for artificial intelligence", "ai department", "artificial intelligence centre"],
        "description": "Official departmental portal of the Centre for Artificial Intelligence at MITS Gwalior.",
        "department": "Centre for Artificial Intelligence",
        "source": "web.mitsgwalior.in",
        "verified": True
    },
    {
        "key": "cse_faculty_profiles",
        "title": "School of Computer Science & Engineering — Faculty Profiles",
        "url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "category": "FACULTY",
        "keywords": ["cse faculty", "computer science faculty", "cse teachers", "cse professors"],
        "description": "Official faculty directory for the School of Computer Science & Engineering.",
        "department": "School of CSE",
        "source": "web.mitsgwalior.in",
        "verified": True
    },
    {
        "key": "iot_faculty_profiles",
        "title": "Centre for Internet of Things — Faculty Profiles",
        "url": "https://web.mitsgwalior.in/faculty-profiles-iot-2",
        "category": "FACULTY",
        "keywords": ["iot faculty", "internet of things faculty", "iot teachers", "iot professors"],
        "description": "Official faculty directory for the Centre for Internet of Things (IoT).",
        "department": "Centre for IoT",
        "source": "web.mitsgwalior.in",
        "verified": True
    }
]


def resolve_institutional_link(query: str) -> Optional[Dict[str, Any]]:
    """
    Resolves natural language queries to exact verified institutional links and portals.
    Returns matched portal record or None if no high-confidence link matches.
    """
    q_lower = query.lower().strip()

    # Exact token/phrase scoring
    best_match = None
    max_score = 0

    for item in INSTITUTIONAL_LINK_REGISTRY:
        score = 0
        for kw in item["keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                # Word boundary match gets high score
                score = max(score, len(kw) * 2)
            elif kw in q_lower:
                score = max(score, len(kw))

        if score > max_score and score >= 4:
            max_score = score
            best_match = item

    return best_match
