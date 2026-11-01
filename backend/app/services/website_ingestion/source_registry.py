from typing import List, Dict, Any

OFFICIAL_MITS_DOMAINS = [
    "web.mitsgwalior.in",
    "ams.mitsgwalior.in",
    "mis.mitsgwalior.in",
    "ims.mitsgwalior.in",
    "moodle.mitsgwalior.in",
    "alumni.mitsgwalior.in",
    "nec.mitsgwalior.in",
    "osm.mitsapps.in",
    "rrs.mitsapps.in"
]

INITIAL_INSTITUTIONAL_SOURCES = [
    {
        "name": "MITS Gwalior Main Website",
        "domain": "web.mitsgwalior.in",
        "base_url": "https://web.mitsgwalior.in/",
        "category": "MITS_MAIN",
        "crawl_depth": 2,
        "crawl_frequency_hours": 24,
        "auth_required": False,
        "allowed_patterns": ["*mitsgwalior.in*"],
        "excluded_patterns": ["*login*", "*signin*", "*admin*", "*password*"],
        "description": "Official institutional portal of Madhav Institute of Technology & Science, Gwalior (M.P.)"
    },
    {
        "name": "MITS Centre for Artificial Intelligence",
        "domain": "web.mitsgwalior.in",
        "base_url": "https://web.mitsgwalior.in/academics/departments/centre-of-artificial-intelligence",
        "category": "DEPARTMENT",
        "crawl_depth": 2,
        "crawl_frequency_hours": 12,
        "auth_required": False,
        "allowed_patterns": ["*centre-of-artificial-intelligence*", "*cai*"],
        "excluded_patterns": [],
        "description": "Academic and administrative pages of the Centre for Artificial Intelligence at MITS."
    },
    {
        "name": "CAI Faculty Profiles Directory",
        "domain": "web.mitsgwalior.in",
        "base_url": "https://web.mitsgwalior.in/faculty-profiles-cai",
        "category": "FACULTY",
        "crawl_depth": 1,
        "crawl_frequency_hours": 24,
        "auth_required": False,
        "allowed_patterns": ["*faculty*"],
        "excluded_patterns": [],
        "description": "Verified official faculty profiles, research areas, and designations for CAI."
    },
    {
        "name": "CAI Programmes Offered",
        "domain": "web.mitsgwalior.in",
        "base_url": "https://web.mitsgwalior.in/programmes-offered-cai",
        "category": "ACADEMIC",
        "crawl_depth": 1,
        "crawl_frequency_hours": 24,
        "auth_required": False,
        "allowed_patterns": ["*programme*"],
        "excluded_patterns": [],
        "description": "Undergraduate, postgraduate, and doctoral degree programmes in AI."
    },
    {
        "name": "CAI Research Areas & Laboratories",
        "domain": "web.mitsgwalior.in",
        "base_url": "https://web.mitsgwalior.in/research-areas-cai",
        "category": "RESEARCH",
        "crawl_depth": 1,
        "crawl_frequency_hours": 24,
        "auth_required": False,
        "allowed_patterns": ["*research*"],
        "excluded_patterns": [],
        "description": "Official research focus areas, publications, and laboratory facilities."
    },
    {
        "name": "MITS Academic Calendar",
        "domain": "web.mitsgwalior.in",
        "base_url": "https://web.mitsgwalior.in/index.php/academic-calendar",
        "category": "CALENDAR",
        "crawl_depth": 1,
        "crawl_frequency_hours": 12,
        "auth_required": False,
        "allowed_patterns": ["*calendar*"],
        "excluded_patterns": [],
        "description": "Official semester schedules, MST dates, holidays, and registration windows."
    },
    {
        "name": "MITS Academic Management System (AMS)",
        "domain": "ams.mitsgwalior.in",
        "base_url": "https://ams.mitsgwalior.in/",
        "category": "AMS",
        "crawl_depth": 1,
        "crawl_frequency_hours": 24,
        "auth_required": False,
        "allowed_patterns": ["https://ams.mitsgwalior.in/"],
        "excluded_patterns": ["*dashboard*", "*student*", "*faculty*", "*attendance*", "*marks*"],
        "description": "Public landing page and documentation of the MITS Academic Management System. Strictly public help and domain metadata only."
    }
]

OFFICIAL_PORTALS_CATALOGUE = [
    {
        "name": "MITS Institute Website",
        "category": "ACADEMIC",
        "official_url": "https://web.mitsgwalior.in/",
        "domain": "web.mitsgwalior.in",
        "purpose": "Official public website of MITS Gwalior for academic news, circulars, department overviews, syllabus schemes and faculty information.",
        "services_description": "Public notices, academic schemes, institute history, faculty profiles, research initiatives, committee directories, downloads.",
        "auth_required": False,
        "contains_confidential_records": False,
        "integration_status": "ACTIVE_ADAPTER"
    },
    {
        "name": "Academic Management System (AMS)",
        "category": "ACADEMIC",
        "official_url": "https://ams.mitsgwalior.in/",
        "domain": "ams.mitsgwalior.in",
        "purpose": "Student and faculty academic tracking platform for daily attendance recording, course observation reports, continuous assessment and mentoring.",
        "services_description": "Attendance tracking, daily timetable scheduling, internal assessment marking, observation reports, faculty mentoring records.",
        "auth_required": True,
        "contains_confidential_records": True,
        "integration_status": "APPROVED_IMPORT_ONLY"
    },
    {
        "name": "Management Information System (MIS)",
        "category": "FACULTY_STAFF",
        "official_url": "https://mis.mitsgwalior.in/",
        "domain": "mis.mitsgwalior.in",
        "purpose": "Administrative human resources and employee portal for faculty and staff service records, leaves, payroll and departmental approvals.",
        "services_description": "Faculty leave applications, service book management, administrative workflow approvals, payroll slips.",
        "auth_required": True,
        "contains_confidential_records": True,
        "integration_status": "LINK_ONLY"
    },
    {
        "name": "Integrated Management System (IMS)",
        "category": "STUDENT_SERVICES",
        "official_url": "https://ims.mitsgwalior.in/",
        "domain": "ims.mitsgwalior.in",
        "purpose": "Student administrative portal for fee receipts, semester course registration, hostel allotment and identity cards.",
        "services_description": "Online semester fee payment, enrolment confirmation, no-dues clearance, student identity verification.",
        "auth_required": True,
        "contains_confidential_records": True,
        "integration_status": "LINK_ONLY"
    },
    {
        "name": "MITS MOODLE Learning Management",
        "category": "LEARNING",
        "official_url": "https://moodle.mitsgwalior.in/",
        "domain": "moodle.mitsgwalior.in",
        "purpose": "Online learning management system for course materials, lab assignments, quizzes, lecture slides and assignment submissions.",
        "services_description": "Course courseware distribution, online quiz submissions, discussion forums, lab assignment uploads.",
        "auth_required": True,
        "contains_confidential_records": False,
        "integration_status": "LINK_ONLY"
    },
    {
        "name": "MITS Alumni Network Portal",
        "category": "ALUMNI",
        "official_url": "https://alumni.mitsgwalior.in/",
        "domain": "alumni.mitsgwalior.in",
        "purpose": "Global alumni directory and engagement portal facilitating mentorship, alumni meets, career connections and institutional endowments.",
        "services_description": "Alumni directory search, mentorship programs, alumni event registration, career opportunities.",
        "auth_required": True,
        "contains_confidential_records": False,
        "integration_status": "LINK_ONLY"
    },
    {
        "name": "NEC Registration Portal",
        "category": "STUDENT_SERVICES",
        "official_url": "https://nec.mitsgwalior.in/",
        "domain": "nec.mitsgwalior.in",
        "purpose": "National Entrepreneurship Challenge registration and incubation tracking for student start-ups, innovation pitches and patents.",
        "services_description": "Start-up project registrations, innovation challenge applications, incubation funding tracking.",
        "auth_required": False,
        "contains_confidential_records": False,
        "integration_status": "LINK_ONLY"
    },
    {
        "name": "Online Answer-sheet Evaluation System (OSM)",
        "category": "EXAMINATION",
        "official_url": "https://osm.mitsapps.in/",
        "domain": "osm.mitsapps.in",
        "purpose": "Secure digital evaluation system used by authorized examiners to digitally mark end-semester examination answer booklets.",
        "services_description": "Digitized on-screen evaluation of examination answer scripts, mark tabulation, moderator review.",
        "auth_required": True,
        "contains_confidential_records": True,
        "integration_status": "LINK_ONLY"
    },
    {
        "name": "Result & Answer-sheet Retrieval Portal (RRS)",
        "category": "EXAMINATION",
        "official_url": "https://rrs.mitsapps.in/",
        "domain": "rrs.mitsapps.in",
        "purpose": "Student examination result retrieval and evaluated answer-sheet copy download system.",
        "services_description": "Semester grade card access, answer-sheet PDF copy downloads, revaluation application submission.",
        "auth_required": True,
        "contains_confidential_records": True,
        "integration_status": "APPROVED_IMPORT_ONLY"
    }
]
