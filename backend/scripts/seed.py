import os
import sys
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import SessionLocal, engine, Base
import backend.app.models as m
from backend.app.models.identity import Role, User, UserRole, AuthenticationAccount
from backend.app.models.academic import Institution, Department, Programme, Branch, AcademicYear, Semester
from backend.app.models.student import StudentProfile, StudentSkill, Project, ProfileVisibility
from backend.app.models.faculty import FacultyProfile, FacultyPublication, FacultyResearchInterest
from backend.app.models.application import Application, ApplicationVersionModel, ApplicationStatusHistory
from backend.app.models.communication import Conversation, Message, Notification
from backend.app.models.academic_records import TimetableEntry, ExaminationEntry, AcademicCalendarEntry, ResultRecord, ResultSubject
from backend.app.models.document import InstitutionalDocument, DocumentAudience, DocumentPublicationHistory
from backend.app.services.audit_service import log_audit_event


def seed_database():
    db = SessionLocal()
    try:
        print("[*] Creating all tables if not present...")
        Base.metadata.create_all(bind=engine)

        print("[*] Seeding Roles...")
        roles = {}
        for role_name, desc in [
            ("SUPER_ADMIN", "Institutional Super Administrator with full configuration authority"),
            ("FACULTY", "Teaching and research faculty member"),
            ("STUDENT", "Enrolled university student")
        ]:
            r = db.query(Role).filter(Role.name == role_name).first()
            if not r:
                r = Role(name=role_name, description=desc, is_demo=False)
                db.add(r)
                db.flush()
            roles[role_name] = r

        print("[*] Seeding Institution & Department...")
        mits = db.query(Institution).filter(Institution.code == "MITS").first()
        if not mits:
            mits = Institution(
                name="Madhav Institute of Technology & Science",
                code="MITS",
                description="Deemed-to-be-University / Autonomous Government-aided Institution, Gwalior",
                website_url="https://web.mitsgwalior.in",
                address="Racecourse Road, Gola ka Mandir, Gwalior, Madhya Pradesh 474005",
                is_demo=False
            )
            db.add(mits)
            db.flush()

        cai = db.query(Department).filter(Department.code == "CAI").first()
        if not cai:
            cai = Department(
                institution_id=mits.id,
                name="Centre for Artificial Intelligence",
                code="CAI",
                overview="The Centre for Artificial Intelligence at MITS Gwalior drives undergraduate and postgraduate technical education in AI, Machine Learning, Deep Learning, Robotics, and Cognitive Computing.",
                vision="To become a renowned hub of excellence in Artificial Intelligence education, innovation, and ethical technological development.",
                mission="Imparting rigorous foundation in AI algorithms, nurturing practical problem solving, and fostering interdisciplinary research.",
                head_of_department="Dr. Rajni Ranjan Singh Makwana",
                is_demo=False
            )
            db.add(cai)
            db.flush()

        # Programmes & Branches
        programmes_data = [
            ("B.Tech IT (AI & Robotics)", "B.Tech", 4, ["AI & Robotics"]),
            ("B.Tech Artificial Intelligence", "B.Tech", 4, ["Artificial Intelligence"]),
            ("B.Tech AI & Machine Learning", "B.Tech", 4, ["AI & Machine Learning"]),
            ("B.Tech AI & Data Science", "B.Tech", 4, ["AI & Data Science"]),
            ("M.Tech Artificial Intelligence", "M.Tech", 2, ["Artificial Intelligence (PG)"])
        ]
        for prog_name, deg, dur, branches in programmes_data:
            p = db.query(Programme).filter(Programme.name == prog_name).first()
            if not p:
                p = Programme(
                    department_id=cai.id,
                    name=prog_name,
                    degree=deg,
                    duration_years=dur,
                    description=f"{deg} curriculum offered by Centre for AI",
                    is_demo=False
                )
                db.add(p)
                db.flush()
                for b_name in branches:
                    b = Branch(
                        programme_id=p.id,
                        name=b_name,
                        code=b_name[:4].upper(),
                        is_demo=False
                    )
                    db.add(b)

        # Academic Year
        ay = db.query(AcademicYear).filter(AcademicYear.year_label == "2026-2027").first()
        if not ay:
            ay = AcademicYear(year_label="2026-2027", is_current=1, is_demo=False)
            db.add(ay)
            db.flush()

        print("[*] Seeding Initial Super Admin...")
        super_admin_email = "utsavkumawat05@gmail.com"
        admin_user = db.query(User).filter(User.email == super_admin_email).first()
        if not admin_user:
            admin_user = User(
                email=super_admin_email,
                full_name="Utsav Kumawat",
                picture_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80",
                designation="Lead Platform Architect & Super Administrator",
                department_name="Centre for Artificial Intelligence",
                is_active=True,
                is_demo=False
            )
            db.add(admin_user)
            db.flush()
            db.add(UserRole(user_id=admin_user.id, role_id=roles["SUPER_ADMIN"].id, is_demo=False))
            db.add(AuthenticationAccount(
                user_id=admin_user.id,
                provider="local_dev",
                provider_user_id=super_admin_email,
                email=super_admin_email,
                is_demo=False
            ))

        print("[*] Seeding Official MITS Faculty Data (Centre for AI)...")
        # 1. Dr. Mausam Chouksey (Prominent mentor)
        chouksey = db.query(FacultyProfile).filter(FacultyProfile.name == "Dr. Mausam Chouksey").first()
        if not chouksey:
            # Create user account
            u_chouksey = User(
                email="dr.mausam.chouksey@mitsgwalior.in",
                full_name="Dr. Mausam Chouksey",
                designation="Assistant Professor",
                department_name="Centre for Artificial Intelligence & ECE",
                picture_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
                is_active=True,
                is_demo=False
            )
            db.add(u_chouksey)
            db.flush()
            db.add(UserRole(user_id=u_chouksey.id, role_id=roles["FACULTY"].id, is_demo=False))

            chouksey = FacultyProfile(
                user_id=u_chouksey.id,
                name="Dr. Mausam Chouksey",
                designation="Assistant Professor",
                department="Centre for Artificial Intelligence & ECE",
                qualification="Ph.D. (Electronics & Communication Engineering), M.Tech, B.E.",
                bio="Dr. Mausam Chouksey is an Assistant Professor affiliated with the Centre for Artificial Intelligence at MITS Gwalior. His research centers on computer vision, underwater image processing, deep neural network optimization, and soft computing algorithms. Designated Faculty Mentor for PocketUni.",
                office_location="Room 204, Centre for Artificial Intelligence Complex",
                office_hours="Monday & Wednesday, 2:30 PM – 4:30 PM",
                email_public="dr.mausam.chouksey@mitsgwalior.in",
                phone_public="+91-751-2409388",
                photo_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
                source_url="https://web.mitsgwalior.in/faculty-profiles-cai/dr-mausam-chouksey",
                verification_status="VERIFIED_OFFICIAL_SOURCE",
                is_mentor=True,
                is_demo=False
            )
            db.add(chouksey)
            db.flush()

            # Research areas
            for area in ["Image Processing & Segmentation", "Soft Computing", "Underwater Image Enhancement", "Deep Learning", "Meta-heuristic Optimization"]:
                db.add(FacultyResearchInterest(faculty_profile_id=chouksey.id, area=area, is_demo=False))

            # Verified publications
            pubs_chouksey = [
                ("A fast technique for image segmentation based on two meta-heuristic algorithms", "Multimedia Tools and Applications, Springer", 2020, "10.1007/s11042-020-09312-x"),
                ("A multiverse optimization based colour image segmentation using variational mode decomposition", "Expert Systems with Applications, Elsevier", 2021, "10.1016/j.eswa.2021.115421"),
                ("A joint entropy for image segmentation based on quasi opposite multiverse optimization", "Multimedia Tools and Applications, Springer", 2021, "10.1007/s11042-021-10822-7"),
                ("Optimal luminosity and contrast reformation system for retinal fundus image intensity enhancement", "Wireless Personal Communications, Springer", 2024, "10.1007/s11277-024-11029-4")
            ]
            for t, j, y, d in pubs_chouksey:
                db.add(FacultyPublication(faculty_profile_id=chouksey.id, title=t, journal=j, year=y, doi=d, is_demo=False))

        # 2. Additional official verified CAI faculty members
        official_faculty_list = [
            ("Dr. Rajni Ranjan Singh Makwana", "Associate Professor & Head / Dean", "rajni.makwana@mitsgwalior.in", ["Artificial Intelligence", "Machine Learning", "Optimization"], "Ph.D., M.Tech"),
            ("Dr. Mir Shahnawaz Ahmad", "Assistant Professor & Head (School of AI)", "shahnawaz.ahmad@mitsgwalior.in", ["Deep Learning", "Cognitive Computing", "Data Science"], "Ph.D. (CSE)"),
            ("Dr. Anu Sayal", "Associate Professor", "anu.sayal@mitsgwalior.in", ["Data Analytics", "Computational Intelligence"], "Ph.D."),
            ("Dr. Arun Kumar", "Assistant Professor", "arun.kumar.cai@mitsgwalior.in", ["Robotics", "Intelligent Systems"], "Ph.D."),
            ("Dr. Pawan Dubey", "Assistant Professor", "pawan.dubey@mitsgwalior.in", ["Machine Learning", "Pattern Recognition"], "Ph.D."),
            ("Dr. Tej Singh", "Assistant Professor", "tej.singh@mitsgwalior.in", ["Computer Vision", "Deep Learning"], "Ph.D."),
            ("Dr. Bhagat Singh Raghuwanshi", "Assistant Professor", "bhagat.raghuwanshi@mitsgwalior.in", ["Natural Language Processing", "Big Data"], "Ph.D."),
            ("Dr. Sunil Kumar Shukla", "Assistant Professor", "sunil.shukla@mitsgwalior.in", ["Cloud AI", "Edge Computing"], "Ph.D."),
            ("Dr. Vibha Tiwari", "Assistant Professor", "vibha.tiwari@mitsgwalior.in", ["Bioinformatics", "Data Mining"], "Ph.D."),
            ("Dr. Shubha Mishra", "Assistant Professor", "shubha.mishra@mitsgwalior.in", ["AI Ethics", "Neural Networks"], "Ph.D."),
            ("Dr. Abhishek Bhatt", "Assistant Professor", "abhishek.bhatt@mitsgwalior.in", ["Autonomous Systems", "Reinforcement Learning"], "Ph.D."),
            ("Dr. Shipra Shukla", "Assistant Professor", "shipra.shukla@mitsgwalior.in", ["Speech Processing", "AI Applications"], "Ph.D."),
            ("Dr. Rahul Kumar Sharma", "Assistant Professor", "rahul.sharma.cai@mitsgwalior.in", ["Generative AI", "Computer Networks"], "Ph.D."),
            ("Dr. Hardev Singh Pal", "Assistant Professor", "hardev.pal@mitsgwalior.in", ["Computer Vision", "Image Processing"], "Ph.D."),
            ("Dr. Sumit Dhariwal", "Assistant Professor", "sumit.dhariwal@mitsgwalior.in", ["Cyber-Physical Systems", "IoT"], "Ph.D."),
            ("Dr. Neelam Arya", "Assistant Professor", "neelam.arya@mitsgwalior.in", ["Machine Learning", "Soft Computing"], "Ph.D."),
            ("Dr. Anurag Singh Tomar", "Assistant Professor", "anurag.tomar@mitsgwalior.in", ["Artificial Intelligence", "Signal Processing"], "Ph.D."),
            ("Dr. Satyam Omar", "Assistant Professor", "satyam.omar@mitsgwalior.in", ["Distributed AI", "Algorithm Design"], "Ph.D."),
            ("Dr. Neeraj Mishra", "Assistant Professor", "neeraj.mishra@mitsgwalior.in", ["Information Security", "AI in Cybersecurity"], "Ph.D."),
            ("Rishabh Deo Pandey", "Assistant Professor", "rishabh.pandey@mitsgwalior.in", ["Robotic Operating Systems", "Embedded AI"], "M.Tech"),
            ("Dr. Nandkishor Joshi", "Assistant Professor", "nandkishor.joshi@mitsgwalior.in", ["Applied Mathematics in AI", "Optimization"], "Ph.D.")
        ]

        for fname, fdesig, femail, fareas, fqual in official_faculty_list:
            existing_f = db.query(FacultyProfile).filter(FacultyProfile.name == fname).first()
            if not existing_f:
                u_fac = User(
                    email=femail,
                    full_name=fname,
                    designation=fdesig,
                    department_name="Centre for Artificial Intelligence",
                    picture_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
                    is_active=True,
                    is_demo=False
                )
                db.add(u_fac)
                db.flush()
                db.add(UserRole(user_id=u_fac.id, role_id=roles["FACULTY"].id, is_demo=False))

                fprof = FacultyProfile(
                    user_id=u_fac.id,
                    name=fname,
                    designation=fdesig,
                    department="Centre for Artificial Intelligence",
                    qualification=fqual,
                    bio=f"{fname} serves as {fdesig} at the Centre for Artificial Intelligence, MITS Gwalior. Actively involved in teaching core and elective AI curricula and student research projects.",
                    office_location="Centre for Artificial Intelligence Building",
                    office_hours="Tuesday & Thursday, 3:00 PM – 5:00 PM",
                    email_public=femail,
                    photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
                    source_url="https://web.mitsgwalior.in/faculty-profiles-cai",
                    verification_status="VERIFIED_OFFICIAL_SOURCE",
                    is_mentor=False,
                    is_demo=False
                )
                db.add(fprof)
                db.flush()

                for area in fareas:
                    db.add(FacultyResearchInterest(faculty_profile_id=fprof.id, area=area, is_demo=False))

        print("[*] Seeding Synthetic Student Data (Section 7: is_demo = true, DEMO- roll numbers)...")
        sample_students = [
            {
                "name": "Mahi Gupta",
                "email": "mahi.gupta@example.invalid",
                "roll": "DEMO-0901AI231012",
                "branch": "B.Tech Artificial Intelligence",
                "year": 3,
                "bio": "3rd-year AI student focused on NLP and LLM evaluation benchmarks. Passionate about participating in national hackathons and building developer tools.",
                "skills": [("PyTorch", "Advanced"), ("HuggingFace", "Advanced"), ("Python", "Advanced"), ("FastAPI", "Intermediate")],
                "interests": ["Natural Language Processing", "Fine-tuning LLMs", "Hackathons"],
                "lookingFor": "Team for Smart India Hackathon (seeking frontend & UI designers)."
            },
            {
                "name": "Ankur Singh Yadav",
                "email": "ankur.yadav@example.invalid",
                "roll": "DEMO-0901ML231018",
                "branch": "B.Tech AI & Machine Learning",
                "year": 3,
                "bio": "Competitive programmer and ML engineer. Skilled in computer vision and graph neural networks. 5-star on CodeChef.",
                "skills": [("C++", "Advanced"), ("Computer Vision", "Advanced"), ("OpenCV", "Intermediate"), ("PyTorch", "Intermediate")],
                "interests": ["Competitive Programming", "Robotics Vision", "Algorithms"],
                "lookingFor": "Collaborators for AI research paper implementations."
            },
            {
                "name": "Mahi Choudhary",
                "email": "mahi.choudhary@example.invalid",
                "roll": "DEMO-0901DS241022",
                "branch": "B.Tech AI & Data Science",
                "year": 2,
                "bio": "2nd-year Data Science enthusiast exploring data pipelines, PostgreSQL, and statistical machine learning models.",
                "skills": [("SQL", "Advanced"), ("Pandas", "Advanced"), ("Scikit-Learn", "Intermediate"), ("Python", "Advanced")],
                "interests": ["Data Science", "Analytics", "Open Source"],
                "lookingFor": "Study group for Kaggle competitions and backend dev."
            },
            {
                "name": "Aarav Sharma",
                "email": "aarav.sharma@example.invalid",
                "roll": "DEMO-0901AR231001",
                "branch": "B.Tech IT (AI & Robotics)",
                "year": 2,
                "bio": "2nd-year AI & Robotics student. Passionate about building fast web interfaces and embedded robotics systems.",
                "skills": [("React", "Advanced"), ("TypeScript", "Advanced"), ("Flutter", "Intermediate"), ("Tailwind CSS", "Advanced")],
                "interests": ["Web Development", "Mobile Apps", "Hackathons", "Design Systems"],
                "lookingFor": "Teammates for Smart India Hackathon 2026."
            },
            {
                "name": "Devansh Joshi",
                "email": "devansh.joshi@example.invalid",
                "roll": "DEMO-0901AR221034",
                "branch": "B.Tech IT (AI & Robotics)",
                "year": 3,
                "bio": "3rd-year robotics software specialist. Working with ROS2, Gazebo simulation, and autonomous quadrupeds.",
                "skills": [("ROS2", "Advanced"), ("Python", "Advanced"), ("C++", "Intermediate"), ("Linux", "Advanced")],
                "interests": ["Autonomous Navigation", "Robotics", "Simulations"],
                "lookingFor": "Hardware enthusiasts for university robotics team."
            },
            {
                "name": "Meera Patel",
                "email": "meera.patel@example.invalid",
                "roll": "DEMO-0901AI211045",
                "branch": "B.Tech Artificial Intelligence",
                "year": 4,
                "bio": "Final-year student specializing in deep generative models. Selected for research internship at IIT Indore.",
                "skills": [("Diffusion Models", "Advanced"), ("PyTorch", "Advanced"), ("Python", "Advanced"), ("Docker", "Intermediate")],
                "interests": ["Generative AI", "Medical Imaging", "Research"],
                "lookingFor": "Junior students to mentor in research paper writing."
            }
        ]

        student_users = {}
        for s in sample_students:
            u_stud = db.query(User).filter(User.email == s["email"]).first()
            if not u_stud:
                u_stud = User(
                    email=s["email"],
                    full_name=s["name"],
                    roll_number=s["roll"],
                    branch=s["branch"],
                    year_of_study=str(s["year"]),
                    picture_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80",
                    is_active=True,
                    is_demo=True
                )
                db.add(u_stud)
                db.flush()
                db.add(UserRole(user_id=u_stud.id, role_id=roles["STUDENT"].id, is_demo=True))

                sp = StudentProfile(
                    user_id=u_stud.id,
                    bio=s["bio"],
                    looking_for=s["lookingFor"],
                    open_for_hackathons=True,
                    open_source_contributor=True,
                    competitive_programming=True,
                    availability_hours_per_week=18,
                    interests=s["interests"],
                    domains=[s["branch"]],
                    preferred_roles=["AI Engineer", "Software Engineer"],
                    tech_stack=[sk[0] for sk in s["skills"]],
                    completeness_score=88,
                    is_demo=True
                )
                db.add(sp)
                db.flush()

                db.add(ProfileVisibility(student_profile_id=sp.id, is_public=True, show_contact=False, show_cgpa=False, is_demo=True))

                for sk_name, sk_prof in s["skills"]:
                    db.add(StudentSkill(
                        student_profile_id=sp.id,
                        skill_name=sk_name,
                        proficiency=sk_prof,
                        category="Technical",
                        is_demo=True
                    ))

                # Add sample project
                db.add(Project(
                    student_profile_id=sp.id,
                    title=f"{s['name'].split()[0]}'s Autonomous AI Project",
                    description="Open source research benchmark evaluated across academic test suites.",
                    repo_url="https://github.com/example/pocketuni-demo",
                    live_url="https://pocketuni.mitsgwalior.in",
                    tech_notes=["Python", "FastAPI", "PyTorch"],
                    is_demo=True
                ))

            student_users[s["roll"]] = u_stud

        print("[*] Seeding Official MITS Academic Calendar (Section 9: 2026-2027)...")
        calendar_entries = [
            # 2nd & 3rd Year Calendar
            ("Commencement of Academic Session (Theory & Practical Classes)", "2026-07-15", None, "2nd & 3rd Year", "Session starts across B.Tech AI & Robotics, AI, AIML, and AIDS"),
            ("Registration & Choice-Based Credit System Enrollment", "2026-07-15", "2026-07-22", "2nd & 3rd Year", "Late registration with fee applies thereafter"),
            ("Mid-Semester Test — I (MST-1)", "2026-09-08", "2026-09-12", "2nd & 3rd Year", "Syllabus: Units I & II"),
            ("Internal Attendance Review & Shortage Notice (<75%)", "2026-09-25", None, "2nd & 3rd Year", "Official warning issued by Department Coordinators"),
            ("Mid-Semester Test — II (MST-2)", "2026-10-27", "2026-10-31", "2nd & 3rd Year", "Syllabus: Units III & IV"),
            ("Last Day of Instruction / Teaching Term Closes", "2026-11-20", None, "2nd & 3rd Year", "Remedial doubt clearing sessions"),
            ("Practical Examination & Project Viva-Voce", "2026-11-23", "2026-11-28", "2nd & 3rd Year", "Internal & External evaluations"),
            ("End-Semester Theory Examinations (Autonomous CBCS)", "2026-12-02", "2026-12-18", "2nd & 3rd Year", "Mandatory minimum 75% attendance for admit card generation"),
            ("Winter Vacation", "2026-12-21", "2027-01-03", "2nd & 3rd Year", "Hostels close on Dec 22"),
            ("Commencement of Even Semester (Jan - June 2027)", "2027-01-05", None, "2nd & 3rd Year", "Even semester classes begin"),

            # Final Year Calendar (Distinguished per Section 9)
            ("Final Year Academic Session Commencement & Major Project Allotment", "2026-07-08", None, "Final Year", "Major Project Phase-I guide allocation"),
            ("Campus Placement Pre-Placement Talks (T&P Cell)", "2026-07-20", "2026-08-05", "Final Year", "Onboarding of Marquee & Dream recruiters"),
            ("Mid-Semester Test — I (MST-1 Final Year)", "2026-09-01", "2026-09-05", "Final Year", "Accommodates ongoing placement assessments"),
            ("Major Project Phase-I Progress Review Seminar", "2026-10-14", "2026-10-16", "Final Year", "Presentation before Departmental Review Committee"),
            ("Mid-Semester Test — II (MST-2 Final Year)", "2026-10-20", "2026-10-24", "Final Year", "Theory courses"),
            ("End-Semester Examinations & Project Phase-I Evaluation", "2026-11-25", "2026-12-12", "Final Year", "Conducted on priority for internship joining"),
            ("Mandatory Full-Semester Industry Internship / Project Phase-II Begins", "2027-01-02", None, "Final Year", "For students opting for off-campus research/internship")
        ]

        for act, s_dt, e_dt, grp, rem in calendar_entries:
            db.add(AcademicCalendarEntry(
                activity=act,
                start_date=s_dt,
                end_date=e_dt,
                applicable_semester=grp,
                academic_year="2026-2027",
                remarks=rem,
                is_demo=False
            ))

        print("[*] Seeding Timetable Entries (Centre for AI)...")
        timetable_entries = [
            ("Monday", "09:30 AM", "10:30 AM", "Deep Neural Networks (CS-3101)", "CS-3101", "Dr. Mausam Chouksey", "LH-101", "B.Tech", "B.Tech Artificial Intelligence", "5th Sem"),
            ("Monday", "10:30 AM", "11:30 AM", "Optimization Techniques in AI", "AI-3102", "Dr. Rajni Ranjan Singh Makwana", "LH-101", "B.Tech", "B.Tech Artificial Intelligence", "5th Sem"),
            ("Tuesday", "09:30 AM", "11:30 AM", "Computer Vision & Robotics Lab", "AR-2104", "Dr. Mausam Chouksey", "AI-Lab-1", "B.Tech", "B.Tech IT (AI & Robotics)", "3rd Sem"),
            ("Wednesday", "11:30 AM", "12:30 PM", "Natural Language Processing", "AI-3103", "Dr. Bhagat Singh Raghuwanshi", "LH-102", "B.Tech", "B.Tech Artificial Intelligence", "5th Sem"),
            ("Thursday", "02:00 PM", "04:00 PM", "Deep Learning Laboratory", "AI-3105", "Dr. Mausam Chouksey", "NVIDIA GPU Cluster Lab", "B.Tech", "B.Tech Artificial Intelligence", "5th Sem"),
            ("Friday", "10:30 AM", "11:30 AM", "Ethics in Artificial Intelligence", "AI-3106", "Dr. Shubha Mishra", "LH-101", "B.Tech", "B.Tech Artificial Intelligence", "5th Sem")
        ]
        for day, st, et, sub, sc, fac, rm, prog, br, sem in timetable_entries:
            db.add(TimetableEntry(
                day=day,
                start_time=st,
                end_time=et,
                subject=sub,
                subject_code=sc,
                faculty_name=fac,
                room=rm,
                programme=prog,
                branch=br,
                semester=sem,
                academic_year="2026-2027",
                is_demo=True
            ))

        print("[*] Seeding Examination Datesheets...")
        exam_entries = [
            ("Deep Neural Networks", "CS-3101", "2026-12-03", "10:00 AM – 01:00 PM", "End-Semester", "5th Sem", "B.Tech", "B.Tech Artificial Intelligence"),
            ("Optimization Techniques in AI", "AI-3102", "2026-12-07", "10:00 AM – 01:00 PM", "End-Semester", "5th Sem", "B.Tech", "B.Tech Artificial Intelligence"),
            ("Natural Language Processing", "AI-3103", "2026-12-11", "10:00 AM – 01:00 PM", "End-Semester", "5th Sem", "B.Tech", "B.Tech Artificial Intelligence"),
            ("Computer Vision & Image Processing", "AR-2104", "2026-12-04", "10:00 AM – 01:00 PM", "End-Semester", "3rd Sem", "B.Tech", "B.Tech IT (AI & Robotics)")
        ]
        for sub, sc, dt, tm, et, sem, prog, br in exam_entries:
            db.add(ExaminationEntry(
                subject=sub,
                subject_code=sc,
                date=dt,
                time=tm,
                examination_type=et,
                semester=sem,
                programme=prog,
                branch=br,
                academic_year="2026-2027",
                is_demo=True
            ))

        print("[*] Seeding Sample Sensitive Results (Section 17: Strict demo privacy)...")
        sample_results = [
            ("DEMO-0901AR231001", "Aarav Sharma", "B.Tech IT (AI & Robotics)", "3rd Sem", 8.45, 8.32, [
                ("AR-2101", "Data Structures & Algorithms", 4.0, 86.0, 100.0, "A+"),
                ("AR-2102", "Object Oriented Programming in C++", 4.0, 82.0, 100.0, "A"),
                ("AR-2103", "Robotics Kinematics & Actuators", 3.0, 78.0, 100.0, "B+"),
                ("AR-2104", "Discrete Mathematical Structures", 3.0, 88.0, 100.0, "A+"),
                ("AR-2105", "Data Structures Laboratory", 1.5, 92.0, 100.0, "O")
            ]),
            ("DEMO-0901AI231012", "Mahi Gupta", "B.Tech Artificial Intelligence", "5th Sem", 9.12, 8.94, [
                ("CS-3101", "Deep Neural Networks", 4.0, 94.0, 100.0, "O"),
                ("AI-3102", "Optimization Techniques in AI", 4.0, 91.0, 100.0, "O"),
                ("AI-3103", "Natural Language Processing", 4.0, 88.0, 100.0, "A+"),
                ("AI-3105", "Deep Learning Laboratory", 2.0, 96.0, 100.0, "O")
            ]),
            ("DEMO-0901ML231018", "Ankur Singh Yadav", "B.Tech AI & Machine Learning", "5th Sem", 8.80, 8.71, [
                ("CS-3101", "Deep Neural Networks", 4.0, 90.0, 100.0, "A+"),
                ("ML-3102", "Machine Learning Algorithms", 4.0, 86.0, 100.0, "A+"),
                ("ML-3103", "Computer Vision Foundations", 4.0, 85.0, 100.0, "A+"),
                ("ML-3104", "Competitive Programming Studio", 2.0, 95.0, 100.0, "O")
            ]),
            ("DEMO-0901DS241022", "Mahi Choudhary", "B.Tech AI & Data Science", "3rd Sem", 8.60, 8.52, [
                ("DS-2101", "Applied Probability & Statistics", 4.0, 87.0, 100.0, "A+"),
                ("DS-2102", "Database Management Systems", 4.0, 89.0, 100.0, "A+"),
                ("DS-2103", "Data Wrangling with Python", 3.0, 92.0, 100.0, "O")
            ])
        ]

        for roll, sname, br, sem, sgpa, cgpa, subs in sample_results:
            rr = ResultRecord(
                roll_number=roll,
                student_name=sname,
                programme="B.Tech",
                branch=br,
                academic_year="2026-2027",
                semester=sem,
                examination_session="June 2026",
                sgpa=sgpa,
                cgpa=cgpa,
                result_status="PASS",
                is_demo=True
            )
            db.add(rr)
            db.flush()
            for sc, sn, cr, mo, mm, gr in subs:
                db.add(ResultSubject(
                    result_record_id=rr.id,
                    subject_code=sc,
                    subject_name=sn,
                    credits=cr,
                    marks_obtained=mo,
                    maximum_marks=mm,
                    grade=gr,
                    is_demo=True
                ))

        print("[*] Seeding Demo Applications & Notifications...")
        aarav_user = student_users.get("DEMO-0901AR231001")
        if aarav_user and chouksey:
            app_leave = Application(
                student_id=aarav_user.id,
                faculty_id=chouksey.user_id,
                title="Leave Application (Smart India Hackathon Internal Round)",
                type="leave",
                status="approved",
                current_version_no=1,
                content="""Date: October 20, 2026

To,
The Head of Department,
Centre for Artificial Intelligence,
Madhav Institute of Technology & Science, Gwalior

Subject: Application for Grant of Leave — Reg.

Respected Sir,

I am writing to formally request leave of absence from October 22 to October 24, 2026, due to severe seasonal fever, followed by college representation at the regional Smart India Hackathon internal round.

I have arranged with my peers to cover all missed lectures and lab experiments. Medical prescription is attached for your kind consideration.

Thanking you.

Yours faithfully,

Aarav Sharma
Roll Number: DEMO-0901AR231001
Branch: B.Tech IT (AI & Robotics)""",
                is_demo=True
            )
            db.add(app_leave)
            db.flush()

            db.add(ApplicationStatusHistory(
                application_id=app_leave.id,
                from_status="created",
                to_status="sent",
                actor_user_id=aarav_user.id,
                actor_name="Aarav Sharma",
                note="Submitted application to Dr. Mausam Chouksey",
                is_demo=True
            ))
            db.add(ApplicationStatusHistory(
                application_id=app_leave.id,
                from_status="sent",
                to_status="approved",
                actor_user_id=chouksey.user_id,
                actor_name="Dr. Mausam Chouksey",
                note="Approved. Ensure missed laboratory experiments are submitted in the next slot.",
                is_demo=True
            ))

            # Notification
            db.add(Notification(
                user_id=aarav_user.id,
                type="application_approved",
                title="Application Approved",
                body="Dr. Mausam Chouksey approved your Leave Application.",
                application_id=app_leave.id,
                is_demo=True
            ))

        db.commit()
        print("[+] Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"[-] Seeding error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
