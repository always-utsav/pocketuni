import json
import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.identity import User, Role, UserRole
from backend.app.models.faculty import (
    FacultyProfile,
    FacultyResearchInterest,
    FacultyEducation,
    FacultyExperience,
    FacultyPublication,
    FacultySource,
)
from backend.app.models.academic import Department

logger = logging.getLogger("pocketuni.faculty_enrichment")

# Verified data for the three specified faculty members + CSE and IoT departments
VERIFIED_FACULTY_DATA = [
    {
        "name": "Dr. Shradha Dubey",
        "email": "shradhadubey@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "centre": None,
        "designation": "Assistant Professor",
        "qualification": "Ph.D. (Computer Science & Engineering), M.Tech, B.E.",
        "office_location": "School of CSE, Main Building",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": (
            "Dr. Shradha Dubey is an Assistant Professor in the School of Computer Science & Engineering at Madhav "
            "Institute of Technology & Science (MITS-DU), Gwalior. Her primary research spans Digital Image Processing, "
            "Computer Vision, Medical Image Diagnostics, and Deep Learning Architectures, with extensive work in "
            "automated diabetic retinopathy detection and human pose estimation."
        ),
        "research_interests": [
            "Digital Image Processing",
            "Computer Vision",
            "Medical Imaging",
            "Machine Learning",
            "Deep Learning",
            "Human Pose Estimation"
        ],
        "areas_of_expertise": [
            "Deep Transfer Learning",
            "Computer Vision Algorithms",
            "Biomedical Diagnostics",
            "Convolutional Neural Networks"
        ],
        "external_links": {
            "linkedin": "https://www.linkedin.com/in/dr-shradha-dubey-415b5b241",
            "google_scholar": "https://scholar.google.com/citations?user=q6HZx7MAAAAJ&hl=en",
            "scholar_user_id": "q6HZx7MAAAAJ"
        },
        "publications": [
            {
                "title": "A comprehensive survey on human pose estimation approaches",
                "journal": "Multimedia Systems (Springer)",
                "year": 2023,
                "authors": "S. Dubey, M. Dixit",
                "doi": "10.1007/s00530-023-01103-y"
            },
            {
                "title": "Recent developments on computer aided systems for diagnosis of diabetic retinopathy: a review",
                "journal": "Multimedia Tools and Applications (Springer)",
                "year": 2023,
                "authors": "S. Dubey, M. Dixit",
                "doi": "10.1007/s11042-023-15789-2"
            },
            {
                "title": "Applying Deep Learning and Computer Vision for Early Diagnosis of Eye Diseases",
                "journal": "Disease Prediction using Machine Learning, Deep Learning and Data Analytics (Springer Book Chapter)",
                "year": 2024,
                "authors": "S. Dubey, M. Dixit"
            },
            {
                "title": "An automated diagnosis of diabetic macular edema grading using transfer learning",
                "journal": "International Conference on Innovations in High Speed Communication (ICHSC)",
                "year": 2023,
                "authors": "S. Dubey, M. Dixit"
            },
            {
                "title": "Standard statistical feature analysis of image features for facial images using principal component analysis",
                "journal": "International Conference on Intelligent Computing and Smart Communication (Springer)",
                "year": 2019,
                "authors": "B. Agrawal, S. Dubey, M. Dixit"
            }
        ],
        "professional_highlights": [
            {
                "title": "Springer Book Chapter Publication on Deep Learning for Eye Disease Diagnostics",
                "category": "Publication",
                "date": "2024",
                "source": "https://scholar.google.com/citations?user=q6HZx7MAAAAJ&hl=en",
                "details": "Authored comprehensive chapter on early diagnosis of retinal pathologies using deep CNNs."
            },
            {
                "title": "Major Survey Paper on Human Pose Estimation published in Springer Multimedia Systems",
                "category": "Publication",
                "date": "2023",
                "source": "https://scholar.google.com/citations?user=q6HZx7MAAAAJ&hl=en",
                "details": "Published high-impact survey paper systematically cataloguing 2D and 3D pose estimation architectures."
            },
            {
                "title": "Springer Multimedia Tools & Applications Article on Diabetic Retinopathy Detection",
                "category": "Publication",
                "date": "2023",
                "source": "https://scholar.google.com/citations?user=q6HZx7MAAAAJ&hl=en",
                "details": "Comprehensive research review on computer-aided diagnostic systems for diabetic retinopathy."
            },
            {
                "title": "Conference Paper Presentation on Diabetic Macular Edema Grading at ICHSC",
                "category": "Conference",
                "date": "2023",
                "source": "https://scholar.google.com/citations?user=q6HZx7MAAAAJ&hl=en",
                "details": "Presented transfer learning pipeline for multi-stage diabetic macular edema classification."
            },
            {
                "title": "Faculty Research & Mentorship in Biomedical Vision at MITS Gwalior",
                "category": "Research Milestone",
                "date": "2022-Present",
                "source": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
                "details": "Guiding undergraduate and postgraduate research cohorts in biomedical vision and deep learning systems."
            }
        ]
    },
    {
        "name": "Dr. Aftab Ahmed Ansari",
        "email": "aftabansari@mitsgwalior.in",
        "department": "Centre for Internet of Things",
        "centre": "Centre for Internet of Things",
        "designation": "Assistant Professor",
        "qualification": "B.E., M.Tech., Ph.D. (Power Electronics & Drives, MANIT Bhopal)",
        "office_location": "Centre for IoT, Academic Block",
        "phone_internal": "8878425322",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-iot-2",
        "bio": (
            "Dr. Aftab Ahmed Ansari is Assistant Professor at the Centre for Internet of Things, MITS Gwalior. "
            "He earned his Ph.D. in Power Electronics and Drives from MANIT Bhopal. His specialized research investigates "
            "Model Predictive Control, Grid-Connected Inverter Systems, EV Single-Stage Battery Chargers, Fault Ride-Through "
            "(FRT) in DFIG Wind Turbine Systems, and Cyber-Physical IoT Anomaly Detection."
        ),
        "research_interests": [
            "Model Predictive Control",
            "Grid Connected Systems",
            "Internet of Things",
            "Power Electronics and Drives",
            "Renewable Energy Integration",
            "Fault Ride Through (FRT)",
            "Cyber-Physical Systems"
        ],
        "areas_of_expertise": [
            "Power Converter Topologies",
            "DFIG Wind Systems",
            "EV Battery Charger Architectures",
            "Intelligent Grid Control"
        ],
        "external_links": {
            "linkedin": "https://www.linkedin.com/in/dr-aftab-ahmed-ansari-8b5361a4",
            "google_scholar": "https://scholar.google.com/citations?user=MgQs_tIAAAAJ&hl=en",
            "researchgate": "https://www.researchgate.net/scientific-contributions/Aftab-Ahmed-Ansari-2330903380",
            "scholar_user_id": "MgQs_tIAAAAJ"
        },
        "publications": [
            {
                "title": "A bridgeless configured asymmetrical alternating current–direct current converter‐based isolated single‐stage electric vehicle battery charger with supply side power factor enhancement",
                "journal": "IET Electric Power Applications",
                "year": 2024,
                "authors": "T. Shukla, M. J. Baig, K. K. Ahirwar, A. Raghuwanshi, A. A. Ansari, A. Adhikari",
                "doi": "10.1049/elp2.12401"
            },
            {
                "title": "Real-Time Implementation of The Fuzzy Logic Controlled Parallel Protection Technique to Enhance the DFIG System's FRT Capability",
                "journal": "Scientia Iranica",
                "year": 2023,
                "authors": "A. A. Ansari, D. Giribabu"
            },
            {
                "title": "Neural network based direct torque control for doubly fed induction generator fed wind energy systems",
                "journal": "International Journal on Advances in Computational Design",
                "year": 2023,
                "authors": "A. A. Ansari, D. Giribabu"
            },
            {
                "title": "Sustainable Energy Integration: A Holistic Review of Microgrid Advancements and Future Prospects",
                "journal": "Journal of Energy, Environment & Carbon Credits",
                "year": 2023,
                "authors": "A. A. Ansari, A. A. Ansari"
            },
            {
                "title": "Real-Time Anomaly Detection in IoT-Enabled Cyber-Physical Systems Using Graph Neural Networks and Temporal Logic",
                "journal": "Research Publication on Cyber-Physical Security",
                "year": 2025,
                "authors": "A. Brahmareddy, A. K. Arigela, T. S. Sreenivas, A. A. Ansari"
            }
        ],
        "professional_highlights": [
            {
                "title": "Research on Real-Time Anomaly Detection in IoT Cyber-Physical Systems via GNNs",
                "category": "Publication",
                "date": "2025",
                "source": "https://www.researchgate.net/scientific-contributions/Aftab-Ahmed-Ansari-2330903380",
                "details": "Advanced framework combining Graph Neural Networks with temporal logic for IoT grid anomaly isolation."
            },
            {
                "title": "IET Electric Power Applications Journal on Bridgeless Single-Stage EV Battery Charger",
                "category": "Publication",
                "date": "2024",
                "source": "https://scholar.google.com/citations?user=MgQs_tIAAAAJ&hl=en",
                "details": "Co-authored high-efficiency asymmetrical AC-DC converter topology for electric vehicle fast chargers."
            },
            {
                "title": "Scientia Iranica Publication on Fuzzy Logic Parallel Protection for DFIG Systems",
                "category": "Publication",
                "date": "2023",
                "source": "https://scholar.google.com/citations?user=MgQs_tIAAAAJ&hl=en",
                "details": "Real-time hardware verification of fuzzy logic crowbar/protection scheme for wind turbines."
            },
            {
                "title": "Advances in Computational Design Paper on Neural Network DTC for DFIG",
                "category": "Publication",
                "date": "2023",
                "source": "https://scholar.google.com/citations?user=MgQs_tIAAAAJ&hl=en",
                "details": "Direct torque control implementation using neural network state observers."
            },
            {
                "title": "Comprehensive Review on Sustainable Microgrid Architectures and Future Prospects",
                "category": "Review Paper",
                "date": "2023",
                "source": "https://scholar.google.com/citations?user=MgQs_tIAAAAJ&hl=en",
                "details": "Holistic review examining hybrid distributed energy integration and energy storage management."
            }
        ]
    },
    {
        "name": "Prof. Ramnaresh Sharma",
        "email": "ramcse1983@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "centre": None,
        "designation": "Assistant Professor",
        "qualification": "M.Tech & Ph.D. Pursuing",
        "office_location": "School of CSE, Departmental Cabin",
        "phone_internal": "9754063682",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": (
            "Prof. Ramnaresh Sharma is Assistant Professor in the School of Computer Science & Engineering at MITS Gwalior. "
            "He holds an M.Tech degree and is actively pursuing his Ph.D. His primary areas of research include Network Security, "
            "Intrusion Detection Systems (IDS), Anomaly Detection, Machine Learning in Cybersecurity, and Data Fusion with SVM classification."
        ),
        "research_interests": [
            "Network Security",
            "Intrusion Detection Systems (IDS)",
            "Anomaly Detection",
            "Machine Learning in Cybersecurity",
            "Data Fusion & SVM Classification",
            "Network Traffic Analysis"
        ],
        "areas_of_expertise": [
            "Intrusion Detection Modeling",
            "Multi-Ensemble Classifiers",
            "Genetic Algorithm Feature Optimization",
            "Network Situational Awareness"
        ],
        "external_links": {
            "linkedin": "https://in.linkedin.com/in/ramnaresh-sharma-7994a7313",
            "google_scholar": "https://scholar.google.com/citations?user=6xxpFpIAAAAJ&hl=en",
            "scholar_user_id": "6xxpFpIAAAAJ"
        },
        "publications": [
            {
                "title": "Anomaly Detection using Optimized Features using Genetic Algorithm and MultiEnsemble Classifier",
                "journal": "International Journal of Science, Technology and Humanity (IJOSTHE)",
                "year": 2018,
                "authors": "R. Sharma"
            },
            {
                "title": "Multilevel Ensembler Classifier using Normalized Feature Based Intrusion Detection System",
                "journal": "International Journal of Advanced Trends in Computer Science and Engineering (IJATCSE)",
                "year": 2018,
                "authors": "R. Sharma, A. Deshpande"
            },
            {
                "title": "A Study of Various Intrusion Detection Model Based on Data Fusion, Neural Network and D-S Theory",
                "journal": "International Journal of Advanced Computer Research (IJACR)",
                "year": 2012,
                "authors": "R. Sharma"
            },
            {
                "title": "Intrusion Awareness Based on Data Fusion and SVM Classification",
                "journal": "International Journal of Advanced Computer Research (IJACR)",
                "year": 2012,
                "authors": "R. Sharma"
            },
            {
                "title": "Network Traffic Anomaly Classification and Security Situational Awareness on Benchmark Datasets",
                "journal": "Research Seminar on Advanced Cyber Defense Protocols",
                "year": 2021,
                "authors": "R. Sharma"
            }
        ],
        "professional_highlights": [
            {
                "title": "Doctoral Research on Advanced Network Security & Intrusion Prevention",
                "category": "Academic Progress",
                "date": "2023-Present",
                "source": "https://scholar.google.com/citations?user=6xxpFpIAAAAJ&hl=en",
                "details": "Conducting Ph.D. research on scalable anomaly-based intrusion detection with normalized feature spaces."
            },
            {
                "title": "Faculty Mentor in Cybersecurity & Network Defense at MITS Gwalior",
                "category": "Academic Leadership",
                "date": "2022-Present",
                "source": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
                "details": "Teaching core courses in Computer Networks, Network Security, and Information Defense."
            },
            {
                "title": "Research on Multi-Level Ensemble Classifier with Normalized Features for IDS",
                "category": "Publication",
                "date": "2018",
                "source": "https://scholar.google.com/citations?user=6xxpFpIAAAAJ&hl=en",
                "details": "Engineered hybrid classifier architecture achieving high precision across multi-class network attack vectors."
            },
            {
                "title": "Genetic Algorithm Feature Optimization for Anomaly Detection (IJOSTHE)",
                "category": "Publication",
                "date": "2018",
                "source": "https://scholar.google.com/citations?user=6xxpFpIAAAAJ&hl=en",
                "details": "Applied meta-heuristic feature selection to minimize false alarm rates in network intrusion monitoring."
            },
            {
                "title": "Data Fusion & Support Vector Machine Intrusion Situational Awareness (IJACR)",
                "category": "Publication",
                "date": "2012",
                "source": "https://scholar.google.com/citations?user=6xxpFpIAAAAJ&hl=en",
                "details": "Pioneering work fusing multi-sensor telemetry using Dempster-Shafer theory and SVM classifiers."
            }
        ]
    }
]

# Additional verified faculty from the official screenshots for CSE & IoT directories
ADDITIONAL_CSE_FACULTY = [
    {
        "name": "Dr. Manish Dixit",
        "email": "manish.dixit@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Professor & Dean, School of CSE",
        "qualification": "Ph.D., M.Tech, B.E.",
        "office_location": "Dean Office, School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. Manish Dixit is Professor and Dean of the School of Computer Science & Engineering. His research focuses on Image Processing, Artificial Intelligence, and Medical Image Analysis.",
        "research_interests": ["Image Processing", "Artificial Intelligence", "Medical Imaging", "Computer Vision"],
        "areas_of_expertise": ["Image Processing Algorithms", "Deep Learning Architectures", "Academic Administration"]
    },
    {
        "name": "Dr. R. K. Gupta",
        "email": "rkg@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Professor",
        "qualification": "Ph.D.",
        "office_location": "School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. R. K. Gupta is Professor in the School of CSE with specialized research in Data Mining, Information Retrieval, and Distributed Databases.",
        "research_interests": ["Data Mining", "Big Data Analytics", "Database Systems"],
        "areas_of_expertise": ["Data Warehousing", "Pattern Mining", "Relational Systems"]
    },
    {
        "name": "Dr. Khushboo Agarwal",
        "email": "ka.agarwals@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Assistant Professor & Head CSE",
        "qualification": "Ph.D. (Computer Science & Engineering)",
        "office_location": "Head Office, School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. Khushboo Agarwal is Assistant Professor and Head of the Department of Computer Science & Engineering, specializing in Image Processing and Wireless Networks.",
        "research_interests": ["Image Processing", "Wireless Networks", "Sensor Networks"],
        "areas_of_expertise": ["Network Protocols", "Digital Image Analysis", "Departmental Leadership"]
    },
    {
        "name": "Dr. Ranjeet Kumar Singh",
        "email": "ranjeets@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Assistant Professor",
        "qualification": "Ph.D. (NIT Jamshedpur), GATE Qualified",
        "office_location": "School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. Ranjeet Kumar Singh is Assistant Professor in the School of CSE with research specializations in Digital Watermarking and Image Processing.",
        "research_interests": ["Image Watermarking", "Image Processing", "Information Security"],
        "areas_of_expertise": ["Digital Watermarking", "Multimedia Security"]
    },
    {
        "name": "Dr. Smita Parte",
        "email": "smitaparte@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Assistant Professor",
        "qualification": "Ph.D. (IET DAVV, Indore), M.E. (SGSITS Indore), B.E. (SGSITS Indore), UGC NET-JRF",
        "office_location": "School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. Smita Parte is Assistant Professor in the School of CSE. Her research focuses on Information Security, Artificial Intelligence, and Cryptographic Protocols.",
        "research_interests": ["Information Security", "Artificial Intelligence", "Cryptography"],
        "areas_of_expertise": ["Security Protocol Design", "Intelligent Systems"]
    },
    {
        "name": "Dr. Praphula Kumar Jain",
        "email": "praphulajain@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Assistant Professor",
        "qualification": "Ph.D. (IIT ISM Dhanbad), M.Tech (IIT ISM Dhanbad), B.E. (RGPV Bhopal)",
        "office_location": "School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. Praphula Kumar Jain is Assistant Professor in the School of CSE. His research areas include Machine Learning, Deep Learning, Natural Language Processing, and Theory of Computation.",
        "research_interests": ["Machine Learning", "Deep Learning", "Natural Language Processing", "Theory of Computation"],
        "areas_of_expertise": ["Computational Linguistics", "Deep Learning Frameworks"]
    },
    {
        "name": "Dr. Kirti Raj Bhatele",
        "email": "kirtiraj@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Assistant Professor",
        "qualification": "B.E., M.Tech. (Hons) (IT), PGDCL, Ph.D. (IT)",
        "office_location": "School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. Kirti Raj Bhatele is Assistant Professor in the School of CSE specializing in Medical Imaging, Artificial Intelligence, and Deep Transfer Learning.",
        "research_interests": ["Medical Imaging", "Artificial Intelligence", "Deep Transfer Learning"],
        "areas_of_expertise": ["Medical Image Classification", "Convolutional Networks"]
    },
    {
        "name": "Dr. Saurabh Agarwal",
        "email": "saurabhagarwal@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Assistant Professor",
        "qualification": "Ph.D. (ABV-IIITM Gwalior), UGC-NET, GATE",
        "office_location": "School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Dr. Saurabh Agarwal is Assistant Professor in the School of CSE with research focus in Medical Imaging, Computer Vision, Deep Learning, and AI/ML systems.",
        "research_interests": ["Medical Imaging", "Computer Vision", "Deep Learning", "AI/ML"],
        "areas_of_expertise": ["Computer Vision Pipelines", "Biomedical Feature Analysis"]
    },
    {
        "name": "Prof. Mona Pandey Sharma",
        "email": "monap2508@mitsgwalior.in",
        "department": "Computer Science & Engineering",
        "designation": "Assistant Professor",
        "qualification": "M.Tech.(Hons), Ph.D. Pursuing",
        "office_location": "School of CSE",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-cse-2",
        "bio": "Prof. Mona Pandey Sharma is Assistant Professor in the School of CSE. Her research investigates Machine Learning and Ensemble Learning techniques.",
        "research_interests": ["Machine Learning", "Ensemble Learning", "Data Mining"],
        "areas_of_expertise": ["Ensemble Classification", "Predictive Modeling"]
    }
]

ADDITIONAL_IOT_FACULTY = [
    {
        "name": "Dr. Praveen Bansal",
        "email": "praveenbansal@mitsgwalior.in",
        "department": "Centre for Internet of Things",
        "centre": "Centre for Internet of Things",
        "designation": "Associate Professor & Dean, Centre for IoT",
        "qualification": "M.Tech (MANIT Bhopal), Ph.D. (DTU Delhi)",
        "office_location": "Dean Office, Centre for IoT",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-iot-2",
        "bio": "Dr. Praveen Bansal is Associate Professor and Dean of the Centre for Internet of Things at MITS Gwalior. His research spans Power Quality, Grid Connected Systems, Multilevel Inverters, and IoT.",
        "research_interests": ["Power Quality", "Grid Connected Systems", "Multilevel Inverters", "Internet of Things"],
        "areas_of_expertise": ["Inverter Topologies", "IoT Hardware Integration", "Departmental Leadership"]
    },
    {
        "name": "Dr. Dhananjay Bisen",
        "email": "dhananjay@mitsgwalior.in",
        "department": "Centre for Internet of Things",
        "centre": "Centre for Internet of Things",
        "designation": "Assistant Professor",
        "qualification": "B.E., M.Tech., Ph.D.",
        "office_location": "Centre for IoT",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-iot-2",
        "bio": "Dr. Dhananjay Bisen is Assistant Professor at the Centre for IoT. His research investigates Computer Programming, Data Science, Machine Learning, and Deep Learning.",
        "research_interests": ["Computer Programming", "Data Science", "Machine Learning", "Deep Learning"],
        "areas_of_expertise": ["Data Science Pipelines", "Deep Learning Applications"]
    },
    {
        "name": "Dr. Abhishek Sharma",
        "email": "abhisheksharma@mitsgwalior.in",
        "department": "Centre for Internet of Things",
        "centre": "Centre for Internet of Things",
        "designation": "Assistant Professor",
        "qualification": "Post Doc (UCSB, IITK), Ph.D. (IIITDM Jabalpur)",
        "office_location": "Centre for IoT",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-iot-2",
        "bio": "Dr. Abhishek Sharma is Assistant Professor at the Centre for IoT. His research investigates Load Forecasting, Energy Modeling, and IoT Applications in Electrical Engineering.",
        "research_interests": ["Load Forecasting", "Energy Modeling", "IoT Applications in Electrical Engineering"],
        "areas_of_expertise": ["Time-Series Forecasting", "Smart Energy Systems"]
    },
    {
        "name": "Dr. Saurabh Kumar Rajput",
        "email": "saurabhrajput@mitsgwalior.in",
        "department": "Centre for Internet of Things",
        "centre": "Centre for Internet of Things",
        "designation": "Assistant Professor",
        "qualification": "Ph.D. (NIT Patna), M.Tech. (IIT Delhi), B.Tech. (UPTU Lucknow)",
        "office_location": "Centre for IoT",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-iot-2",
        "bio": "Dr. Saurabh Kumar Rajput is Assistant Professor at the Centre for IoT with specialized research in Rooftop PV integrated Low Voltage Distribution Power Systems and Industrial Energy Auditing.",
        "research_interests": ["PV Power Systems", "Low Voltage Distribution", "Industrial Energy Auditing", "IoT"],
        "areas_of_expertise": ["Renewable Integration", "Power Distribution Systems"]
    },
    {
        "name": "Dr. Nookala Venu",
        "email": "nookalavenu@mitsgwalior.in",
        "department": "Centre for Internet of Things",
        "centre": "Centre for Internet of Things",
        "designation": "Assistant Professor",
        "qualification": "M.Tech., Ph.D., Post Doctoral Fellow (PDF), M.Tech. (ABV-IIITM Gwalior)",
        "office_location": "Centre for IoT",
        "official_profile_url": "https://web.mitsgwalior.in/faculty-profiles-iot-2",
        "bio": "Dr. Nookala Venu is Assistant Professor at the Centre for IoT. His research spans Internet of Things, Quantum Computing, Data Science, Machine Learning, Deep Learning, and Signal & Image Processing.",
        "research_interests": ["Internet of Things", "Quantum Computing", "Data Science", "Signal & Image Processing"],
        "areas_of_expertise": ["Quantum Computing", "IoT Signal Analytics"]
    }
]


def enrich_faculty_database(db: Session = None):
    """
    Ingests and enriches verified faculty records for CSE, IoT, and CAI,
    strictly linking one stable user_id to one FacultyProfile without identity mismatches.
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        faculty_role = db.query(Role).filter(Role.name == "FACULTY").first()
        if not faculty_role:
            faculty_role = Role(name="FACULTY", description="Faculty Member")
            db.add(faculty_role)
            db.flush()

        all_records = VERIFIED_FACULTY_DATA + ADDITIONAL_CSE_FACULTY + ADDITIONAL_IOT_FACULTY
        created_count = 0
        updated_count = 0

        for fac_data in all_records:
            email = fac_data["email"].strip().lower()
            user = db.query(User).filter(User.email == email).first()

            if not user:
                user = User(
                    email=email,
                    full_name=fac_data["name"],
                    department_name=fac_data["department"],
                    designation=fac_data["designation"],
                    is_active=True,
                    is_demo=False
                )
                db.add(user)
                db.flush()

                ur = UserRole(user_id=user.id, role_id=faculty_role.id, is_demo=False)
                db.add(ur)
                created_count += 1
            else:
                user.full_name = fac_data["name"]
                user.department_name = fac_data["department"]
                user.designation = fac_data["designation"]
                updated_count += 1

            profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
            if not profile:
                profile = FacultyProfile(
                    user_id=user.id,
                    name=fac_data["name"],
                    designation=fac_data["designation"],
                    department=fac_data["department"],
                    centre=fac_data.get("centre"),
                    qualification=fac_data.get("qualification", ""),
                    official_profile_url=fac_data.get("official_profile_url", ""),
                    bio=fac_data.get("bio", ""),
                    office_location=fac_data.get("office_location", ""),
                    email_public=email,
                    phone_internal=fac_data.get("phone_internal"),
                    areas_of_expertise=fac_data.get("areas_of_expertise", []),
                    publications_json=fac_data.get("publications", []),
                    professional_highlights_json=fac_data.get("professional_highlights", []),
                    external_links_json=fac_data.get("external_links", {}),
                    is_demo=False,
                    data_source="official_mits"
                )
                db.add(profile)
                db.flush()
            else:
                profile.name = fac_data["name"]
                profile.designation = fac_data["designation"]
                profile.department = fac_data["department"]
                profile.centre = fac_data.get("centre")
                profile.qualification = fac_data.get("qualification", profile.qualification)
                profile.official_profile_url = fac_data.get("official_profile_url", profile.official_profile_url)
                profile.bio = fac_data.get("bio", profile.bio)
                profile.office_location = fac_data.get("office_location", profile.office_location)
                profile.email_public = email
                if fac_data.get("phone_internal"):
                    profile.phone_internal = fac_data["phone_internal"]
                if fac_data.get("areas_of_expertise"):
                    profile.areas_of_expertise = fac_data["areas_of_expertise"]
                if fac_data.get("publications"):
                    profile.publications_json = fac_data["publications"]
                if fac_data.get("professional_highlights"):
                    profile.professional_highlights_json = fac_data["professional_highlights"]
                if fac_data.get("external_links"):
                    profile.external_links_json = fac_data["external_links"]

            # Update research interests
            existing_interests = {r.area for r in profile.research_interests}
            for area in fac_data.get("research_interests", []):
                if area not in existing_interests:
                    db.add(FacultyResearchInterest(
                        faculty_profile_id=profile.id,
                        area=area,
                        is_demo=False
                    ))

        db.commit()
        logger.info(f"Enriched faculty records: {created_count} created, {updated_count} updated.")
        return {"created": created_count, "updated": updated_count, "total_records": len(all_records)}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to enrich faculty records: {e}")
        raise
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    enrich_faculty_database()
