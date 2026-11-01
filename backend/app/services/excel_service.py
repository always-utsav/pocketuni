import os
import json
import logging
import tempfile
import shutil
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.identity import User, UserRole, Role
from backend.app.models.student import StudentProfile, StudentSkill, Project, ProfileVisibility
from backend.app.models.faculty import FacultyProfile, FacultyResearchInterest
from backend.app.models.roster import RosterImportBatch, ExcelSyncJob

logger = logging.getLogger("pocketuni.excel")

STUDENT_COLUMNS = [
    "institutional_email",
    "google_subject_id",
    "full_name",
    "roll_number",
    "enrolment_number",
    "department",
    "programme",
    "branch",
    "specialization",
    "batch",
    "academic_year",
    "semester",
    "section",
    "date_of_admission",
    "profile_picture",
    "bio",
    "skills",
    "interests",
    "projects",
    "achievements",
    "certifications",
    "experience",
    "resume",
    "LinkedIn",
    "GitHub",
    "portfolio",
    "profile_visibility",
    "created_at",
    "updated_at",
    "is_demo",
    "data_source"
]

FACULTY_COLUMNS = [
    "institutional_email",
    "google_subject_id",
    "faculty_identifier",
    "full_name",
    "designation",
    "department",
    "centre",
    "official_profile_url",
    "research_interests",
    "office_location",
    "office_hours",
    "bio",
    "qualifications",
    "expertise",
    "publications",
    "courses",
    "projects",
    "profile_picture",
    "profile_visibility",
    "created_at",
    "updated_at",
    "is_demo",
    "data_source"
]

SAMPLE_STUDENTS_DATA = [
    {
        "institutional_email": "demo.aarav.sharma@example.invalid",
        "google_subject_id": "google-demo-sub-001",
        "full_name": "Aarav Sharma",
        "roll_number": "DEMO-0901AI231001",
        "enrolment_number": "0901AI231001",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Deep Learning & Edge Computing",
        "batch": "2023-2027",
        "academic_year": "2026-2027",
        "semester": 5,
        "section": "A",
        "date_of_admission": "2023-08-16",
        "profile_picture": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80",
        "bio": "Third-year AI undergraduate building distributed deep learning and embedded robotics pipelines.",
        "skills": "Python, PyTorch, C++, ROS, FastAPI, OpenCV",
        "interests": "Robotics, Generative Vision, Transformer Acceleration",
        "projects": json.dumps([{"title": "EdgeROS Autonomous Rover", "description": "Micro-ROS navigation package on NVIDIA Jetson"}]),
        "achievements": json.dumps(["Finalist Smart India Hackathon 2025", "First Prize CAI TechSprint 2025"]),
        "certifications": json.dumps(["DeepLearning.AI TensorFlow Specialization", "NVIDIA Jetson AI Specialist"]),
        "experience": json.dumps([{"role": "Robotics Lab Lead", "organization": "MITS Robotics Club", "duration": "2024-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_aarav_sharma.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-aarav-sharma",
        "GitHub": "https://github.com/demo-aarav-sharma",
        "portfolio": "https://aarav-sharma.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-15T12:00:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.mahi.gupta@example.invalid",
        "google_subject_id": "google-demo-sub-002",
        "full_name": "Mahi Gupta",
        "roll_number": "DEMO-0901AI231002",
        "enrolment_number": "0901AI231002",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Natural Language Processing",
        "batch": "2023-2027",
        "academic_year": "2026-2027",
        "semester": 5,
        "section": "A",
        "date_of_admission": "2023-08-16",
        "profile_picture": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80",
        "bio": "AI student researching LLM retrieval grounding, domain embeddings, and multilingual RAG pipelines.",
        "skills": "Python, HuggingFace, PyTorch, TypeScript, LangChain, PostgreSQL",
        "interests": "NLP, Conversational Agents, Domain Embeddings",
        "projects": json.dumps([{"title": "IndicText Summarizer", "description": "Hindi and English fine-tuned T5 model for administrative documents"}]),
        "achievements": json.dumps(["Research Grant Student Recipient 2025", "MITS Academic Merit Scholar"]),
        "certifications": json.dumps(["HuggingFace Certified NLP Specialist", "Google Cloud Associate Cloud Engineer"]),
        "experience": json.dumps([{"role": "NLP Intern", "organization": "IndiGen AI Labs", "duration": "Summer 2025"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_mahi_gupta.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-mahi-gupta",
        "GitHub": "https://github.com/demo-mahi-gupta",
        "portfolio": "https://mahi-gupta.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-20T14:30:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.rohan.shrivastava@example.invalid",
        "google_subject_id": "google-demo-sub-003",
        "full_name": "Rohan Shrivastava",
        "roll_number": "DEMO-0901AI231003",
        "enrolment_number": "0901AI231003",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Computer Vision & Medical Imaging",
        "batch": "2023-2027",
        "academic_year": "2026-2027",
        "semester": 5,
        "section": "A",
        "date_of_admission": "2023-08-16",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
        "bio": "Interested in vision-language models, DICOM segmentation and multi-modal clinical diagnostic tools.",
        "skills": "Python, MONAI, PyTorch, Docker, React, Tailwind CSS",
        "interests": "Medical Imaging, Healthcare AI, 3D Reconstruction",
        "projects": json.dumps([{"title": "BrainLesionSeg", "description": "3D UNet pipeline for automated MRI scan analysis"}]),
        "achievements": json.dumps(["Winner MITS CAI HackFest 2024"]),
        "certifications": json.dumps(["Coursera AI for Medicine Specialization"]),
        "experience": json.dumps([{"role": "Undergraduate Researcher", "organization": "CAI Medical Imaging Lab", "duration": "2024-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_rohan.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-rohan-shrivastava",
        "GitHub": "https://github.com/demo-rohan-shrivastava",
        "portfolio": "https://rohan-vision.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-18T10:15:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.ananya.tiwari@example.invalid",
        "google_subject_id": "google-demo-sub-004",
        "full_name": "Ananya Tiwari",
        "roll_number": "DEMO-0901AI241001",
        "enrolment_number": "0901AI241001",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Data Science",
        "specialization": "Data Engineering & Analytics",
        "batch": "2024-2028",
        "academic_year": "2026-2027",
        "semester": 3,
        "section": "B",
        "date_of_admission": "2024-08-10",
        "profile_picture": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80",
        "bio": "Second-year student passionate about large-scale ETL pipelines, streaming architectures and data governance.",
        "skills": "SQL, Python, Apache Kafka, Spark, Pandas, PostgreSQL",
        "interests": "Data Streaming, Distributed Systems, Cloud Warehousing",
        "projects": json.dumps([{"title": "CampusFlow Analytics", "description": "Real-time telemetry ingestion using Kafka and DuckDB"}]),
        "achievements": json.dumps(["Second Rank First-Year Scholastic Award"]),
        "certifications": json.dumps(["Databricks Certified Data Engineer Associate"]),
        "experience": json.dumps([{"role": "Data Analyst", "organization": "MITS Student Data Society", "duration": "2025-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_ananya.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-ananya-tiwari",
        "GitHub": "https://github.com/demo-ananya-tiwari",
        "portfolio": "https://ananya-data.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-22T08:45:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.devansh.jain@example.invalid",
        "google_subject_id": "google-demo-sub-005",
        "full_name": "Devansh Jain",
        "roll_number": "DEMO-0901AI241002",
        "enrolment_number": "0901AI241002",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Reinforcement Learning",
        "batch": "2024-2028",
        "academic_year": "2026-2027",
        "semester": 3,
        "section": "A",
        "date_of_admission": "2024-08-10",
        "profile_picture": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
        "bio": "Building RL environments for autonomous flight, robotics control and continuous action optimization.",
        "skills": "Python, Gymnasium, Stable-Baselines3, C++, PyBullet",
        "interests": "Reinforcement Learning, Quadcopter Control, Physics Simulators",
        "projects": json.dumps([{"title": "DroneGymRL", "description": "Custom Gymnasium environment for multi-agent drone obstacle avoidance"}]),
        "achievements": json.dumps(["HackMITS 2025 AI Track Winner"]),
        "certifications": json.dumps(["Deep RL Bootcamp Certificate"]),
        "experience": json.dumps([{"role": "Aeromodelling Team Member", "organization": "AeroMITS Club", "duration": "2024-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_devansh.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-devansh-jain",
        "GitHub": "https://github.com/demo-devansh-jain",
        "portfolio": "https://devansh-rl.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-12T16:20:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.khushi.patel@example.invalid",
        "google_subject_id": "google-demo-sub-006",
        "full_name": "Khushi Patel",
        "roll_number": "DEMO-0901AI231004",
        "enrolment_number": "0901AI231004",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Full-Stack AI Applications",
        "batch": "2023-2027",
        "academic_year": "2026-2027",
        "semester": 5,
        "section": "A",
        "date_of_admission": "2023-08-16",
        "profile_picture": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        "bio": "Full-stack engineer building intuitive, accessible UI/UX for AI models, agentic workflows and web tools.",
        "skills": "React, TypeScript, Next.js, Node.js, FastAPI, Tailwind CSS",
        "interests": "Generative UI, Web Performance, Human-AI Interaction",
        "projects": json.dumps([{"title": "DocuChat Assistant", "description": "Interactive document querying interface with real-time streaming"}]),
        "achievements": json.dumps(["MITS Best Design Project Award 2025"]),
        "certifications": json.dumps(["Meta Certified Frontend Developer"]),
        "experience": json.dumps([{"role": "Frontend Lead", "organization": "MITS Coding Club", "duration": "2024-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_khushi.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-khushi-patel",
        "GitHub": "https://github.com/demo-khushi-patel",
        "portfolio": "https://khushi-designs.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-19T11:10:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.aditya.verma@example.invalid",
        "google_subject_id": "google-demo-sub-007",
        "full_name": "Aditya Verma",
        "roll_number": "DEMO-0901AI231005",
        "enrolment_number": "0901AI231005",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Cybersecurity & Adversarial ML",
        "batch": "2023-2027",
        "academic_year": "2026-2027",
        "semester": 5,
        "section": "A",
        "date_of_admission": "2023-08-16",
        "profile_picture": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80",
        "bio": "Exploring prompt injection defenses, model poisoning vulnerabilities and verifiable cryptography.",
        "skills": "Python, Linux, Wireshark, Rust, PyTorch, Cryptography",
        "interests": "Adversarial Robustness, Cryptographic Verification, CTFs",
        "projects": json.dumps([{"title": "ShieldLLM Guardrail", "description": "Heuristic and vector-based jailbreak detector for production LLMs"}]),
        "achievements": json.dumps(["Capture The Flag Top 5 Team Member, InCTF 2025"]),
        "certifications": json.dumps(["CompTIA Security+"]),
        "experience": json.dumps([{"role": "Security Analyst", "organization": "MITS Cyber Cell", "duration": "2024-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_aditya.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-aditya-verma",
        "GitHub": "https://github.com/demo-aditya-verma",
        "portfolio": "https://aditya-sec.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-14T09:30:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.tanvi.mishra@example.invalid",
        "google_subject_id": "google-demo-sub-008",
        "full_name": "Tanvi Mishra",
        "roll_number": "DEMO-0901AI241003",
        "enrolment_number": "0901AI241003",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Audio & Speech Processing",
        "batch": "2024-2028",
        "academic_year": "2026-2027",
        "semester": 3,
        "section": "A",
        "date_of_admission": "2024-08-10",
        "profile_picture": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80",
        "bio": "Researching whisper fine-tuning, acoustic phonetics and multi-speaker separation.",
        "skills": "Python, Librosa, Whisper, PyTorch, Torchaudio, SoundFile",
        "interests": "Speech Recognition, Audio Synthesis, Dialect Adaptation",
        "projects": json.dumps([{"title": "BhopaliWhisper", "description": "Low-resource speech-to-text fine-tuning on regional central Indian dialects"}]),
        "achievements": json.dumps(["MITS Young Innovator Recognition 2025"]),
        "certifications": json.dumps(["DeepLearning.AI Audio Processing Specialization"]),
        "experience": json.dumps([{"role": "Student Coordinator", "organization": "CAI Language & Speech Club", "duration": "2025-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_tanvi.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-tanvi-mishra",
        "GitHub": "https://github.com/demo-tanvi-mishra",
        "portfolio": "https://tanvi-speech.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-21T15:00:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.yash.choudhary@example.invalid",
        "google_subject_id": "google-demo-sub-009",
        "full_name": "Yash Choudhary",
        "roll_number": "DEMO-0901AI231006",
        "enrolment_number": "0901AI231006",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "High-Performance Computing",
        "batch": "2023-2027",
        "academic_year": "2026-2027",
        "semester": 5,
        "section": "B",
        "date_of_admission": "2023-08-16",
        "profile_picture": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=300&q=80",
        "bio": "Optimizing CUDA kernels, Triton operations and memory bandwidth for large transformer training clusters.",
        "skills": "C++, CUDA, Triton, Python, OpenMP, MPI, Linux",
        "interests": "GPU Architecture, Parallel Algorithms, Distributed Training",
        "projects": json.dumps([{"title": "FastAttentionCUDA", "description": "Custom FlashAttention kernel implementation with FP16 support"}]),
        "achievements": json.dumps(["First Place ACM Student Chapter Coding Contest 2025"]),
        "certifications": json.dumps(["NVIDIA Fundamentals of Accelerated Computing with CUDA"]),
        "experience": json.dumps([{"role": "Lab Assistant", "organization": "CAI High-Performance Computing Lab", "duration": "2024-Present"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_yash.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-yash-choudhary",
        "GitHub": "https://github.com/demo-yash-choudhary",
        "portfolio": "https://yash-cuda.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-16T17:40:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.sneha.kulkarni@example.invalid",
        "google_subject_id": "google-demo-sub-010",
        "full_name": "Sneha Kulkarni",
        "roll_number": "DEMO-0901AI241004",
        "enrolment_number": "0901AI241004",
        "department": "Centre for Artificial Intelligence",
        "programme": "B.Tech",
        "branch": "Artificial Intelligence and Machine Learning",
        "specialization": "Bioinformatics & Computational Biology",
        "batch": "2024-2028",
        "academic_year": "2026-2027",
        "semester": 3,
        "section": "B",
        "date_of_admission": "2024-08-10",
        "profile_picture": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=300&q=80",
        "bio": "Applying geometric deep learning, AlphaFold pipelines and graph neural networks to protein structure prediction.",
        "skills": "Python, Biopython, PyTorch Geometric, R, Docker",
        "interests": "Protein Folding, GNNs, Computational Genomics",
        "projects": json.dumps([{"title": "ProteinContactGNN", "description": "Graph neural network for residue-residue contact map prediction"}]),
        "achievements": json.dumps(["Bio-AI Junior Fellowship Award 2025"]),
        "certifications": json.dumps(["EMBL-EBI Bioinformatics Workshop Certificate"]),
        "experience": json.dumps([{"role": "Research Intern", "organization": "Computational Biology Working Group", "duration": "Summer 2025"}]),
        "resume": "https://pocketuni.mitsgwalior.in/resumes/demo_sneha.pdf",
        "LinkedIn": "https://linkedin.com/in/demo-sneha-kulkarni",
        "GitHub": "https://github.com/demo-sneha-kulkarni",
        "portfolio": "https://sneha-bio.demo.invalid",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-23T13:20:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    }
]

SAMPLE_FACULTY_DATA = [
    {
        "institutional_email": "demo.dr.mausam.chouksey@example.invalid",
        "google_subject_id": "google-demo-faculty-001",
        "faculty_identifier": "DEMO-FAC-001",
        "full_name": "Dr. Mausam Chouksey",
        "designation": "Assistant Professor",
        "department": "Centre for Artificial Intelligence",
        "centre": "Centre for Artificial Intelligence",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cai",
        "research_interests": "Deep Learning, Generative AI, Natural Language Processing, Machine Vision",
        "office_location": "CAI Block, Room 204",
        "office_hours": "Monday - Thursday 3:00 PM - 5:00 PM",
        "bio": "Dr. Mausam Chouksey is Assistant Professor at the Centre for Artificial Intelligence, specializing in transformer models and edge intelligence.",
        "qualifications": "Ph.D. in Computer Science & Engineering, M.Tech (CSE), B.E. (CSE)",
        "expertise": "Deep Learning Architectures, NLP, AI System Deployment",
        "publications": json.dumps([
            {"title": "Efficient Transformer Attention for Edge Devices", "journal": "IEEE Trans. Consumer Electronics", "year": 2024},
            {"title": "Domain-Grounded RAG Frameworks in Higher Education", "journal": "ACM Computing Surveys", "year": 2025}
        ]),
        "courses": json.dumps(["24252101 - Machine Learning", "27252101 - Deep Learning Systems", "28252101 - AI Project Lab"]),
        "projects": json.dumps([{"title": "MITS Intelligent Assistant Lab", "role": "Lead Faculty Investigator"}]),
        "profile_picture": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-15T12:00:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    },
    {
        "institutional_email": "demo.rajni.makwana@example.invalid",
        "google_subject_id": "google-demo-faculty-002",
        "faculty_identifier": "DEMO-FAC-002",
        "full_name": "Dr. Rajni Ranjan Singh Makwana",
        "designation": "Associate Professor & Head / Dean",
        "department": "Centre for Artificial Intelligence",
        "centre": "Centre for Artificial Intelligence",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cai",
        "research_interests": "Artificial Intelligence, Pattern Recognition, Machine Learning, Cognitive Systems",
        "office_location": "Dean Office, Centre for AI",
        "office_hours": "Tuesday & Friday 2:00 PM - 4:00 PM",
        "bio": "Dr. Rajni Ranjan Singh Makwana serves as Associate Professor and Head of the Centre for Artificial Intelligence at MITS Gwalior.",
        "qualifications": "Ph.D. in Artificial Intelligence, M.Tech, B.Tech",
        "expertise": "Cognitive Computing, Strategic Academic Administration, AI Curriculum Design",
        "publications": json.dumps([
            {"title": "Pattern Recognition in Complex Academic Ecosystems", "journal": "Springer Lecture Notes in CS", "year": 2023},
            {"title": "Autonomous Institutional Decision Support Systems", "journal": "Journal of AI Research", "year": 2024}
        ]),
        "courses": json.dumps(["Artificial Intelligence Foundations", "Cognitive Computing & Robotics"]),
        "projects": json.dumps([{"title": "MITS Centre for AI Excellence Initiative", "role": "Principal Project Director"}]),
        "profile_picture": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
        "profile_visibility": "PUBLIC",
        "created_at": "2026-08-01T09:00:00Z",
        "updated_at": "2026-10-18T10:00:00Z",
        "is_demo": True,
        "data_source": "synthetic_demo"
    }
]


class ExcelService:

    def __init__(self):
        self.students_filepath = os.path.join(os.getcwd(), "pocketuni_students.xlsx")
        self.faculty_filepath = os.path.join(os.getcwd(), "pocketuni_faculty.xlsx")

    def create_initial_sample_workbooks(self) -> Tuple[str, str]:
        """
        Creates pocketuni_students.xlsx with exactly 10 synthetic students
        and pocketuni_faculty.xlsx with synthetic faculty members.
        """
        # 1. Create Student Workbook
        wb_student = openpyxl.Workbook()
        ws_student = wb_student.active
        ws_student.title = "Students_Roster"

        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
        thin_border = Border(
            left=Side(style='thin', color='D1D5DB'),
            right=Side(style='thin', color='D1D5DB'),
            top=Side(style='thin', color='D1D5DB'),
            bottom=Side(style='thin', color='D1D5DB')
        )

        ws_student.append(STUDENT_COLUMNS)
        for col_num in range(1, len(STUDENT_COLUMNS) + 1):
            cell = ws_student.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row_data in SAMPLE_STUDENTS_DATA:
            row = [row_data.get(col, "") for col in STUDENT_COLUMNS]
            ws_student.append(row)

        for row in ws_student.iter_rows(min_row=2, max_row=len(SAMPLE_STUDENTS_DATA) + 1, min_col=1, max_col=len(STUDENT_COLUMNS)):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")

        wb_student.save(self.students_filepath)

        # 2. Create Faculty Workbook
        wb_faculty = openpyxl.Workbook()
        ws_faculty = wb_faculty.active
        ws_faculty.title = "Faculty_Roster"

        faculty_fill = PatternFill(start_color="0F766E", end_color="0F766E", fill_type="solid")
        ws_faculty.append(FACULTY_COLUMNS)
        for col_num in range(1, len(FACULTY_COLUMNS) + 1):
            cell = ws_faculty.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = faculty_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row_data in SAMPLE_FACULTY_DATA:
            row = [row_data.get(col, "") for col in FACULTY_COLUMNS]
            ws_faculty.append(row)

        for row in ws_faculty.iter_rows(min_row=2, max_row=len(SAMPLE_FACULTY_DATA) + 1, min_col=1, max_col=len(FACULTY_COLUMNS)):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")

        wb_faculty.save(self.faculty_filepath)
        logger.info(f"Initialized sample workbooks: {self.students_filepath}, {self.faculty_filepath}")
        return self.students_filepath, self.faculty_filepath

    def preview_workbook(self, file_path: str, entity_type: str) -> Dict[str, Any]:
        """
        Parses and validates an uploaded Excel file, checking headers, syntax and duplicate records.
        """
        expected_cols = STUDENT_COLUMNS if entity_type == "STUDENT" else FACULTY_COLUMNS
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active

        headers = [cell.value for cell in ws[1] if cell.value is not None]
        missing_headers = [col for col in expected_cols if col not in headers]
        if missing_headers:
            return {
                "valid": False,
                "error": f"Missing required columns: {', '.join(missing_headers)}",
                "headers": headers
            }

        total_rows = 0
        valid_rows = 0
        invalid_rows = 0
        preview_records = []
        errors = []
        seen_emails = set()

        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):
                continue
            total_rows += 1
            row_dict = dict(zip(headers, row))
            email = str(row_dict.get("institutional_email") or "").strip().lower()

            row_errors = []
            if not email:
                row_errors.append("Institutional email is missing.")
            elif email in seen_emails:
                row_errors.append(f"Duplicate email '{email}' in spreadsheet.")
            else:
                seen_emails.add(email)

            if entity_type == "STUDENT":
                roll = str(row_dict.get("roll_number") or "").strip()
                if not roll:
                    row_errors.append("Roll number is missing.")

            if row_errors:
                invalid_rows += 1
                errors.append({"row": idx, "email": email, "errors": row_errors})
            else:
                valid_rows += 1
                if len(preview_records) < 10:
                    preview_records.append(row_dict)

        return {
            "valid": len(errors) == 0,
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "preview_records": preview_records,
            "errors": errors
        }

    def import_workbook(
        self,
        db: Session,
        file_path: str,
        entity_type: str,
        imported_by_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transactionally imports validated Excel records into PostgreSQL 18.
        Preserves isolation between demo accounts and real accounts.
        """
        expected_cols = STUDENT_COLUMNS if entity_type == "STUDENT" else FACULTY_COLUMNS
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active
        headers = [cell.value for cell in ws[1] if cell.value is not None]

        created_count = 0
        updated_count = 0
        failed_count = 0
        errors = []

        batch = RosterImportBatch(
            entity_type=entity_type,
            file_name=os.path.basename(file_path),
            file_path=file_path,
            status="PROCESSING",
            imported_by_user_id=imported_by_user_id
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

        try:
            for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):
                    continue
                row_dict = dict(zip(headers, row))
                email = str(row_dict.get("institutional_email") or "").strip().lower()
                if not email:
                    continue

                full_name = str(row_dict.get("full_name") or email.split("@")[0]).strip()
                is_demo = bool(row_dict.get("is_demo") or email.endswith(".invalid"))
                data_source = str(row_dict.get("data_source") or ("synthetic_demo" if is_demo else "official"))

                # Query existing user
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    user = User(
                        email=email,
                        full_name=full_name,
                        picture_url=str(row_dict.get("profile_picture") or ""),
                        google_sub=str(row_dict.get("google_subject_id") or None) if row_dict.get("google_subject_id") else None,
                        is_demo=is_demo,
                        is_active=True
                    )
                    db.add(user)
                    db.flush()

                    # Assign Role
                    role_name = "STUDENT" if entity_type == "STUDENT" else "FACULTY"
                    role_obj = db.query(Role).filter(Role.name == role_name).first()
                    if role_obj:
                        ur = UserRole(user_id=user.id, role_id=role_obj.id, is_demo=is_demo)
                        db.add(ur)
                    created_count += 1
                else:
                    user.full_name = full_name
                    if row_dict.get("profile_picture"):
                        user.picture_url = str(row_dict.get("profile_picture"))
                    updated_count += 1

                # Specific profile creation/update
                if entity_type == "STUDENT":
                    roll_number = str(row_dict.get("roll_number") or "").strip()
                    user.roll_number = roll_number
                    user.branch = str(row_dict.get("branch") or "")
                    user.department_name = str(row_dict.get("department") or "")

                    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
                    if not profile:
                        profile = StudentProfile(
                            user_id=user.id,
                            enrolment_number=str(row_dict.get("enrolment_number") or roll_number),
                            programme=str(row_dict.get("programme") or "B.Tech"),
                            specialization=str(row_dict.get("specialization") or ""),
                            batch=str(row_dict.get("batch") or ""),
                            semester=int(row_dict.get("semester") or 1) if str(row_dict.get("semester") or "").isdigit() else 1,
                            section=str(row_dict.get("section") or "A"),
                            academic_year=str(row_dict.get("academic_year") or "2026-2027"),
                            date_of_admission=str(row_dict.get("date_of_admission") or ""),
                            bio=str(row_dict.get("bio") or ""),
                            github_url=str(row_dict.get("GitHub") or ""),
                            linkedin_url=str(row_dict.get("LinkedIn") or ""),
                            portfolio_url=str(row_dict.get("portfolio") or ""),
                            resume_url=str(row_dict.get("resume") or ""),
                            is_demo=is_demo,
                            data_source=data_source
                        )
                        db.add(profile)
                        db.flush()

                        # Skills parsing
                        skills_str = str(row_dict.get("skills") or "")
                        if skills_str:
                            for sk in [s.strip() for s in skills_str.split(",") if s.strip()]:
                                db.add(StudentSkill(student_profile_id=profile.id, skill_name=sk, proficiency="Intermediate", is_demo=is_demo))

                        # Visibility
                        db.add(ProfileVisibility(student_profile_id=profile.id, is_public=True, show_contact=False, show_cgpa=False, is_demo=is_demo))
                    else:
                        profile.enrolment_number = str(row_dict.get("enrolment_number") or profile.enrolment_number)
                        profile.programme = str(row_dict.get("programme") or profile.programme)
                        profile.specialization = str(row_dict.get("specialization") or profile.specialization)
                        profile.batch = str(row_dict.get("batch") or profile.batch)
                        if str(row_dict.get("semester") or "").isdigit():
                            profile.semester = int(row_dict.get("semester"))
                        profile.section = str(row_dict.get("section") or profile.section)
                        profile.academic_year = str(row_dict.get("academic_year") or profile.academic_year)
                        profile.bio = str(row_dict.get("bio") or profile.bio)

                elif entity_type == "FACULTY":
                    fac_id = str(row_dict.get("faculty_identifier") or "")
                    user.designation = str(row_dict.get("designation") or "")
                    user.department_name = str(row_dict.get("department") or "")

                    fac_profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
                    if not fac_profile:
                        fac_profile = FacultyProfile(
                            user_id=user.id,
                            faculty_identifier=fac_id,
                            name=full_name,
                            designation=str(row_dict.get("designation") or "Assistant Professor"),
                            department=str(row_dict.get("department") or "Centre for Artificial Intelligence"),
                            centre=str(row_dict.get("centre") or "Centre for Artificial Intelligence"),
                            qualification=str(row_dict.get("qualifications") or ""),
                            official_profile_url=str(row_dict.get("official_profile_url") or ""),
                            bio=str(row_dict.get("bio") or ""),
                            office_location=str(row_dict.get("office_location") or ""),
                            office_hours=str(row_dict.get("office_hours") or ""),
                            is_demo=is_demo,
                            data_source=data_source
                        )
                        db.add(fac_profile)
                        db.flush()

                        # Research interests
                        interests_str = str(row_dict.get("research_interests") or "")
                        if interests_str:
                            for area in [a.strip() for a in interests_str.split(",") if a.strip()]:
                                db.add(FacultyResearchInterest(faculty_profile_id=fac_profile.id, area=area, is_demo=is_demo))
                    else:
                        fac_profile.faculty_identifier = fac_id or fac_profile.faculty_identifier
                        fac_profile.designation = str(row_dict.get("designation") or fac_profile.designation)
                        fac_profile.department = str(row_dict.get("department") or fac_profile.department)
                        fac_profile.office_location = str(row_dict.get("office_location") or fac_profile.office_location)
                        fac_profile.office_hours = str(row_dict.get("office_hours") or fac_profile.office_hours)
                        fac_profile.bio = str(row_dict.get("bio") or fac_profile.bio)

            batch.total_records = created_count + updated_count + failed_count
            batch.successful_records = created_count + updated_count
            batch.failed_records = failed_count
            batch.errors_summary = errors
            batch.status = "COMPLETED"
            db.commit()

            return {
                "success": True,
                "batch_id": batch.id,
                "created": created_count,
                "updated": updated_count,
                "failed": failed_count,
                "total": batch.total_records
            }
        except Exception as e:
            db.rollback()
            batch.status = "FAILED"
            batch.errors_summary = [{"error": str(e)}]
            db.commit()
            logger.error(f"Failed to import workbook: {e}")
            raise e

    def export_workbook(self, db: Session, entity_type: str) -> str:
        """
        Exports the current PostgreSQL roster into an Excel workbook.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{entity_type.capitalize()}_Roster"

        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        fill_color = "1F2937" if entity_type == "STUDENT" else "0F766E"
        header_fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

        cols = STUDENT_COLUMNS if entity_type == "STUDENT" else FACULTY_COLUMNS
        ws.append(cols)

        for col_idx in range(1, len(cols) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        if entity_type == "STUDENT":
            students = db.query(StudentProfile).join(User).filter(User.is_demo == True).limit(10).all()
            if len(students) < 10:
                students = db.query(StudentProfile).join(User).limit(10).all()
            for sp in students[:10]:
                u = sp.user
                skills_list = [s.skill_name for s in sp.skills] if sp.skills else []
                row = [
                    u.email if u else "",
                    u.google_sub if u else "",
                    u.full_name if u else "",
                    u.roll_number if u else "",
                    sp.enrolment_number or "",
                    u.department_name if u else "",
                    sp.programme or "",
                    u.branch if u else "",
                    sp.specialization or "",
                    sp.batch or "",
                    sp.academic_year or "",
                    sp.semester or 1,
                    sp.section or "A",
                    sp.date_of_admission or "",
                    u.picture_url if u else "",
                    sp.bio or "",
                    ", ".join(skills_list),
                    ", ".join(sp.interests) if sp.interests else "",
                    json.dumps([{"title": p.title, "description": p.description} for p in sp.projects]) if sp.projects else "[]",
                    json.dumps(sp.achievements) if sp.achievements else "[]",
                    json.dumps(sp.certifications) if sp.certifications else "[]",
                    json.dumps(sp.experience) if sp.experience else "[]",
                    sp.resume_url or "",
                    sp.linkedin_url or "",
                    sp.github_url or "",
                    sp.portfolio_url or "",
                    "PUBLIC" if sp.visibility and sp.visibility.is_public else "PRIVATE",
                    sp.created_at.isoformat() if sp.created_at else "",
                    sp.updated_at.isoformat() if sp.updated_at else "",
                    sp.is_demo,
                    sp.data_source
                ]
                ws.append(row)
        else:
            faculty = db.query(FacultyProfile).join(User, isouter=True).all()
            for fp in faculty:
                u = fp.user
                interests_list = [i.area for i in fp.research_interests] if fp.research_interests else []
                row = [
                    u.email if u else (fp.email_public or ""),
                    u.google_sub if u else "",
                    fp.faculty_identifier or "",
                    fp.name,
                    fp.designation,
                    fp.department,
                    fp.centre or fp.department,
                    fp.official_profile_url or "",
                    ", ".join(interests_list),
                    fp.office_location or "",
                    fp.office_hours or "",
                    fp.bio or "",
                    fp.qualification or "",
                    ", ".join(fp.areas_of_expertise) if fp.areas_of_expertise else "",
                    json.dumps(fp.publications_json) if fp.publications_json else "[]",
                    json.dumps(fp.courses) if fp.courses else "[]",
                    json.dumps(fp.projects_json) if fp.projects_json else "[]",
                    fp.photo_url or "",
                    "PUBLIC",
                    fp.created_at.isoformat() if fp.created_at else "",
                    fp.updated_at.isoformat() if fp.updated_at else "",
                    fp.is_demo,
                    fp.data_source
                ]
                ws.append(row)

        filename = "pocketuni_students.xlsx" if entity_type == "STUDENT" else "pocketuni_faculty.xlsx"
        target_path = os.path.join(os.getcwd(), filename)
        # Atomic file write using temporary file to prevent corruption
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"temp_{os.path.basename(target_path)}")
        wb.save(temp_file)
        shutil.move(temp_file, target_path)
        logger.info(f"Successfully exported roster to {target_path}")
        return target_path

    def sync_user_profile(self, db: Session, user_id: str) -> None:
        """
        Synchronizes a modified user profile directly to the mirrored Excel workbook
        with safe atomic replacement.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        roles = [ur.role.name for ur in user.roles if ur.role]
        entity_type = "FACULTY" if "FACULTY" in roles else "STUDENT"

        job = ExcelSyncJob(
            entity_type=entity_type,
            entity_id=user_id,
            user_email=user.email,
            target_file=f"pocketuni_{entity_type.lower()}s.xlsx",
            status="PROCESSING"
        )
        db.add(job)
        db.commit()

        try:
            self.export_workbook(db, entity_type)
            job.status = "COMPLETED"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as e:
            job.status = "FAILED"
            job.last_error = str(e)
            job.retry_count += 1
            db.commit()
            logger.error(f"Excel sync failed for user {user.email}: {e}")


excel_service = ExcelService()
