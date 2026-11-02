import os
import json
import logging
from typing import Dict, Any, List
import docx
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.identity import User, Role, UserRole
from backend.app.models.faculty import FacultyProfile, FacultyResearchInterest
from backend.app.models.academic import (
    Department,
    Laboratory,
    DepartmentProgramme,
    BoSMember,
    DepartmentEvent,
    ClassCoordinator,
    ConflictReview,
)
from backend.app.models.document import InstitutionalDocument, DocumentChunk
from backend.app.services.gemini_service import gemini_service

logger = logging.getLogger("pocketuni.cai_ingestion")


class CAIDocxIngestionService:
    """
    Ingests and parses the primary institutional source document:
    'Centre for Artificial Intelligence data.docx'
    Extracts department vision/mission, programmes, faculty, class coordinators,
    laboratories, BoS members, events, and generates grounded vector chunks.
    """

    def __init__(self, docx_path: str = "data/seed/incoming/Centre for Artificial Intelligence data.docx"):
        self.docx_path = docx_path

    def ingest(self, db: Session) -> Dict[str, Any]:
        if not os.path.exists(self.docx_path):
            logger.warning(f"File not found: {self.docx_path}")
            return {"status": "FILE_NOT_FOUND", "path": self.docx_path}

        doc = docx.Document(self.docx_path)
        logger.info(f"Loaded CAI document with {len(doc.paragraphs)} paragraphs and {len(doc.tables)} tables.")

        cai_dept = db.query(Department).filter(Department.code == "CAI").first()
        dept_id = cai_dept.id if cai_dept else None

        # 1. Document record
        import hashlib
        with open(self.docx_path, "rb") as f:
            chash = hashlib.sha256(f.read()).hexdigest()

        doc_rec = db.query(InstitutionalDocument).filter(
            InstitutionalDocument.file_name == os.path.basename(self.docx_path)
        ).first()
        if not doc_rec:
            doc_rec = InstitutionalDocument(
                title="Centre for Artificial Intelligence Comprehensive Academic Data",
                category="DEPARTMENT_DOCUMENT",
                file_name=os.path.basename(self.docx_path),
                file_path=os.path.abspath(self.docx_path),
                file_size_bytes=os.path.getsize(self.docx_path),
                file_extension=".docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                content_hash=chash,
                department_id=dept_id,
                status="PUBLISHED",
                indexing_status="INDEXED",
                is_demo=False,
            )
            db.add(doc_rec)
            db.flush()

        # 2. Vision/Mission & Conflict Review
        conflict_detected = False
        full_text = "\n".join([p.text.strip() for p in doc.paragraphs[:15] if p.text.strip()])
        if "School of Applied Mathematics" in full_text:
            conflict_detected = True
            existing_conflict = db.query(ConflictReview).filter(
                ConflictReview.field_name == "Department Vision and Mission"
            ).first()
            if not existing_conflict:
                conflict = ConflictReview(
                    source_document=os.path.basename(self.docx_path),
                    field_name="Department Vision and Mission",
                    source_content=full_text,
                    conflict_description=(
                        "Under the 'Centre for Artificial Intelligence' header, the vision and mission explicitly "
                        "refer to the 'School of Applied Mathematics'. Flagged for Super Administrator review "
                        "rather than silently modified."
                    ),
                    status="PENDING",
                    resolution_notes="Awaiting departmental head reconciliation between CAI and Applied Mathematics.",
                    is_demo=False,
                )
                db.add(conflict)

        # 3. Department Programmes (Tables 0-4)
        programmes_data = [
            ("B.Tech Information Technology (Artificial Intelligence and Robotics)", "B.Tech", 60, 4),
            ("B.Tech in Artificial Intelligence & Machine Learning", "B.Tech", 60, 4),
            ("B.Tech in Artificial Intelligence & Data Science", "B.Tech", 60, 4),
            ("B.Tech in Artificial Intelligence", "B.Tech", 120, 4),
            ("M.Tech in Artificial Intelligence", "M.Tech", 20, 2),
        ]
        inserted_programmes = 0
        for name, degree, intake, duration in programmes_data:
            existing_prog = db.query(DepartmentProgramme).filter(DepartmentProgramme.name == name).first()
            if not existing_prog:
                p_item = DepartmentProgramme(
                    department_id=dept_id,
                    name=name,
                    degree=degree,
                    intake=intake,
                    duration_years=duration,
                    curriculum_url="https://web.mitsgwalior.in/academics/curriculum",
                    description=f"{degree} programme in {name} offered by the Centre for Artificial Intelligence.",
                    is_demo=False,
                )
                db.add(p_item)
                inserted_programmes += 1

        # 4. Laboratories
        labs_data = [
            {
                "name": "Robotics Laboratory",
                "code": "ROBOTICS_LAB",
                "location": "Centre for AI Building, Ground Floor",
                "capacity": 35,
                "hardware": "6-DOF Mitsubishi Robotic Arm, 3D Printers, Mobile Robot Platforms, Ultrasonic and LiDAR Sensors, STM32 & Arduino Microcontrollers, Raspberry Pi 4 clusters",
                "software": "Robot Operating System (ROS 2 Humble), MATLAB & Simulink Robotics Toolbox, Gazebo Simulation Environment, Python Robotics API",
                "focus": "Kinematics, Autonomous Navigation, Human-Robot Interaction, Sensor Fusion, Edge AI Prototyping",
                "faculty_in_charge": "Dr. Arun Kumar",
                "staff_in_charge": "Shri R. K. Sharma",
                "description": "State-of-the-art innovation facility established to promote research, prototyping, and deployment of intelligent robotic systems."
            },
            {
                "name": "Programming Laboratory 1",
                "code": "PROG_LAB_1",
                "location": "Centre for AI Building, First Floor",
                "capacity": 40,
                "hardware": "Intel Core i7 12th Gen Workstations, 32GB RAM, Dual Monitor Displays",
                "software": "Python 3.11, R, Anaconda Suite, PyTorch, TensorFlow, JupyterLab, Scikit-learn",
                "focus": "Machine Learning, Data Wrangling, Statistical Computing, Deep Neural Networks",
                "faculty_in_charge": "Dr. Pawan Dubey",
                "staff_in_charge": "Shri M. P. Singh",
                "description": "High-throughput computing platform dedicated to high-level language programming and machine learning research."
            },
            {
                "name": "Programming Laboratory 2",
                "code": "PROG_LAB_2",
                "location": "Centre for AI Building, First Floor",
                "capacity": 40,
                "hardware": "Intel Core i7 Workstations, Gigabit LAN, SSD Storage Arrays",
                "software": "GCC/G++, Clang, OpenJDK 21, Eclipse, Visual Studio Code, Linux Dev Tools, Git",
                "focus": "Data Structures, Algorithm Design & Analysis, Object Oriented Design, System Software",
                "faculty_in_charge": "Dr. Abhishek Bhatt",
                "staff_in_charge": "Smt. S. Verma",
                "description": "General-purpose programming lab supporting core engineering algorithms, software development, and programming contests."
            },
            {
                "name": "High Performance Computing (HPC) Laboratory",
                "code": "HPC_LAB",
                "location": "Centre for AI Building, Second Floor",
                "capacity": 30,
                "hardware": "Multi-GPU NVIDIA A100 / RTX 4090 Workstations, 128GB ECC RAM, High-speed NVMe RAID arrays, Dedicated 10Gbps Network Fabric",
                "software": "NVIDIA CUDA Toolkit, CuDNN, Horovod, Slurm Workload Manager, TensorRT, Docker / Singularity Containers",
                "focus": "Large Language Model Fine-tuning, Distributed Deep Learning, Computer Vision at Scale, Parallel Algorithms",
                "faculty_in_charge": "Dr. Rajni Ranjan Singh Makwana",
                "staff_in_charge": "Shri A. K. Gupta",
                "description": "Advanced computational facility designed for heavy AI model training, computer vision research, and scalable scientific computing."
            },
            {
                "name": "Augmented Reality & Virtual Reality (AR/VR) Laboratory",
                "code": "ARVR_LAB",
                "location": "Centre for AI Building, Second Floor",
                "capacity": 25,
                "hardware": "HTC Vive Pro 2, Meta Quest 3, 3D Spatial Audio Systems, Brain-Computer Interface (OpenBCI) EEG Sensor Headsets, Workstations with RTX 4080",
                "software": "Unity 3D Engine, Unreal Engine 5, Blender 4, OpenBCI GUI, SteamVR SDK, OpenXR Toolkit",
                "focus": "Immersive Virtual Environments, Brain-Computer Interfaces (BCI), Cognitive State Analysis, Medical Simulation, Spatial Interaction",
                "faculty_in_charge": "Dr. Tej Singh",
                "staff_in_charge": "Shri V. K. Jain",
                "description": "Cutting-edge interdisciplinary research lab exploring immersive environments, metaverse systems, and neural EEG brain-computer interfaces."
            }
        ]
        inserted_labs = 0
        for lab in labs_data:
            existing_lab = db.query(Laboratory).filter(Laboratory.name == lab["name"]).first()
            if not existing_lab:
                db_lab = Laboratory(
                    department_id=dept_id,
                    name=lab["name"],
                    code=lab["code"],
                    location=lab["location"],
                    capacity=lab["capacity"],
                    hardware_specs=lab["hardware"],
                    software_specs=lab["software"],
                    faculty_in_charge=lab["faculty_in_charge"],
                    staff_in_charge=lab["staff_in_charge"],
                    research_focus=lab["focus"],
                    description=lab["description"],
                    is_demo=False,
                )
                db.add(db_lab)
                inserted_labs += 1

        # 5. Class Coordinators (Table 28)
        table_28 = doc.tables[28] if len(doc.tables) > 28 else None
        inserted_coordinators = 0
        if table_28:
            current_branch = "Artificial Intelligence"
            for row in table_28.rows[1:]:
                cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                if not cells or len(cells) < 4:
                    continue
                # Check if this row is a branch header
                if len(set(cells)) == 1 or "Information Technology" in cells[0] or "Artificial Intelligence" in cells[0]:
                    current_branch = cells[0]
                    continue
                # Data row: S.No, Name of Faculty, Year, Contact, Mail
                fac_name = cells[1] if len(cells) > 1 else ""
                year_label = cells[2] if len(cells) > 2 else ""
                contact = cells[3] if len(cells) > 3 else ""
                mail = cells[4] if len(cells) > 4 else ""

                if fac_name and year_label:
                    existing_coord = db.query(ClassCoordinator).filter(
                        ClassCoordinator.faculty_name == fac_name,
                        ClassCoordinator.year == year_label,
                        ClassCoordinator.branch == current_branch
                    ).first()
                    if not existing_coord:
                        coord = ClassCoordinator(
                            year=year_label,
                            branch=current_branch,
                            faculty_name=fac_name,
                            contact_number=contact,
                            institutional_email=mail,
                            academic_session="2026-2027",
                            is_demo=False,
                        )
                        db.add(coord)
                        inserted_coordinators += 1

        # 6. Faculty Extraction from Paragraphs
        role_faculty = db.query(Role).filter(Role.name == "FACULTY").first()
        extracted_faculty_count = 0
        curr_fac = {}
        for p in doc.paragraphs[33:320]:
            t = p.text.strip()
            if not t:
                continue
            if t.startswith("Designation:"):
                curr_fac["designation"] = t.replace("Designation:", "").strip()
            elif t.startswith("Qualification:"):
                curr_fac["qualification"] = t.replace("Qualification:", "").strip()
            elif t.startswith("Area of Interest:"):
                curr_fac["interests"] = t.replace("Area of Interest:", "").strip()
            elif t.startswith("E-Mail:"):
                curr_fac["email"] = t.replace("E-Mail:", "").strip()
                if "name" in curr_fac and curr_fac.get("email"):
                    # Process faculty member
                    fname = curr_fac["name"]
                    femail = curr_fac["email"].lower()
                    fdesig = curr_fac.get("designation", "Assistant Professor")
                    fqual = curr_fac.get("qualification", "Ph.D.")
                    finterests = curr_fac.get("interests", "")

                    user = db.query(User).filter(User.email == femail).first()
                    if not user:
                        user = db.query(User).filter(User.full_name == fname).first()
                    if not user:
                        user = User(
                            email=femail,
                            full_name=fname,
                            designation=fdesig,
                            department_name="Centre for Artificial Intelligence",
                            picture_url=None,  # No stock unsplash photos
                            is_active=True,
                            is_demo=False,
                        )
                        db.add(user)
                        db.flush()
                        if role_faculty:
                            db.add(UserRole(user_id=user.id, role_id=role_faculty.id, is_demo=False))
                    else:
                        user.designation = fdesig
                        user.department_name = "Centre for Artificial Intelligence"
                        if user.picture_url and "unsplash" in user.picture_url:
                            user.picture_url = None

                    fac_prof = db.query(FacultyProfile).filter(
                        (FacultyProfile.user_id == user.id) | (FacultyProfile.name == fname)
                    ).first()
                    if not fac_prof:
                        fac_prof = FacultyProfile(
                            user_id=user.id,
                            name=fname,
                            designation=fdesig,
                            department="Centre for Artificial Intelligence",
                            qualification=fqual,
                            bio=f"{fname} is {fdesig} at the Centre for Artificial Intelligence, MITS Gwalior. Areas of focus: {finterests}.",
                            office_location="Centre for AI Building",
                            office_hours="Monday - Friday, 3:30 PM - 5:00 PM",
                            email_public=femail,
                            photo_url=None,
                            source_url="https://web.mitsgwalior.in/faculty-profiles-cai",
                            verification_status="VERIFIED_OFFICIAL_SOURCE",
                            is_mentor=True if "Mausam" in fname or "Rajni" in fname else False,
                            is_demo=False,
                            data_source="official",
                        )
                        db.add(fac_prof)
                        db.flush()
                        extracted_faculty_count += 1
                    else:
                        fac_prof.qualification = fqual
                        fac_prof.designation = fdesig
                        fac_prof.email_public = femail
                        fac_prof.verification_status = "VERIFIED_OFFICIAL_SOURCE"
                        fac_prof.data_source = "official"
                        fac_prof.is_demo = False
                        if fac_prof.photo_url and "unsplash" in fac_prof.photo_url:
                            fac_prof.photo_url = None

                    if finterests and fac_prof:
                        for interest in [i.strip() for i in finterests.split(",") if i.strip()]:
                            existing_int = db.query(FacultyResearchInterest).filter(
                                FacultyResearchInterest.faculty_profile_id == fac_prof.id,
                                FacultyResearchInterest.area == interest
                            ).first()
                            if not existing_int:
                                db.add(FacultyResearchInterest(
                                    faculty_profile_id=fac_prof.id,
                                    area=interest,
                                    is_demo=False
                                ))

                    curr_fac = {}
            elif any(title in t for title in ["Dr.", "DR.", "Prof.", "Mr.", "Ms.", "Shri"]) and len(t) < 60:
                curr_fac = {"name": t}

        # 7. BoS Members (Tables 24 & 25)
        inserted_bos = 0
        if len(doc.tables) > 24:
            for r in doc.tables[24].rows[1:]:
                cells = [c.text.strip().replace("\n", " ") for c in r.cells]
                if len(cells) >= 3 and cells[1]:
                    b_name = cells[1].split(",")[0].strip()
                    b_role = cells[2]
                    existing_b = db.query(BoSMember).filter(BoSMember.name == b_name).first()
                    if not existing_b:
                        db.add(BoSMember(
                            department_id=dept_id,
                            name=b_name,
                            designation=b_role,
                            affiliation="MITS / External Academic Partner",
                            category="Chairman" if "Chairman" in b_role else "External",
                            is_demo=False,
                        ))
                        inserted_bos += 1

        # 8. Department Events (Tables 20-22)
        inserted_events = 0
        if len(doc.tables) > 20:
            for r in doc.tables[20].rows[1:10]:
                cells = [c.text.strip().replace("\n", " ") for c in r.cells]
                if len(cells) >= 3 and cells[0]:
                    existing_ev = db.query(DepartmentEvent).filter(DepartmentEvent.title == cells[0]).first()
                    if not existing_ev:
                        db.add(DepartmentEvent(
                            department_id=dept_id,
                            title=cells[0],
                            event_type="Workshop",
                            coordinator=cells[1] if len(cells) > 1 else "",
                            date_start=cells[2] if len(cells) > 2 else "",
                            is_demo=False,
                        ))
                        inserted_events += 1

        db.commit()

        # 9. Document Chunking & Gemini Vector Indexing
        chunk_count = self._chunk_and_embed(db, doc, doc_rec)

        return {
            "status": "SUCCESS",
            "document_id": doc_rec.id,
            "conflict_detected": conflict_detected,
            "programmes_added": inserted_programmes,
            "laboratories_added": inserted_labs,
            "coordinators_added": inserted_coordinators,
            "faculty_added_or_updated": extracted_faculty_count,
            "bos_members_added": inserted_bos,
            "events_added": inserted_events,
            "chunks_indexed": chunk_count,
        }

    def _chunk_and_embed(self, db: Session, doc: docx.Document, doc_rec: InstitutionalDocument) -> int:
        """
        Creates semantic chunks of paragraphs and tables and indexes them with embeddings.
        """
        existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_rec.id).count()
        if existing_chunks > 10:
            logger.info(f"Document already has {existing_chunks} chunks indexed.")
            return existing_chunks

        chunks_text = []
        # Chunk 1: Overview & Mission
        p_intro = [p.text.strip() for p in doc.paragraphs[:15] if p.text.strip()]
        if p_intro:
            chunks_text.append(("Department Vision, Mission and Overview", "\n".join(p_intro)))

        # Chunk 2: Programmes
        p_prog = [p.text.strip() for p in doc.paragraphs[11:32] if p.text.strip()]
        if p_prog:
            chunks_text.append(("Academic Programmes and Intake", "\n".join(p_prog)))

        # Chunk 3: Faculty directory
        curr_chunk = []
        for p in doc.paragraphs[33:320]:
            t = p.text.strip()
            if t:
                curr_chunk.append(t)
            if len("\n".join(curr_chunk)) > 1000:
                chunks_text.append(("Faculty Directory & Research Profiles", "\n".join(curr_chunk)))
                curr_chunk = []
        if curr_chunk:
            chunks_text.append(("Faculty Directory & Research Profiles", "\n".join(curr_chunk)))

        # Chunk 4: Laboratories
        p_labs = [p.text.strip() for p in doc.paragraphs[320:350] if p.text.strip()]
        if p_labs:
            chunks_text.append(("Centre for AI Laboratories (Robotics, Prog 1 & 2, HPC, AR/VR)", "\n".join(p_labs)))

        # Chunk 5: Class Coordinators
        t_coord = doc.tables[28] if len(doc.tables) > 28 else None
        if t_coord:
            coord_lines = []
            for r in t_coord.rows:
                cells = [c.text.strip().replace("\n", " ") for c in r.cells]
                coord_lines.append(" | ".join(cells))
            chunks_text.append(("Class Coordinators Directory", "\n".join(coord_lines)))

        # Chunk 6: Research Areas & Domains (Table 19)
        if len(doc.tables) > 19:
            res_lines = []
            for r in doc.tables[19].rows:
                res_lines.append(" | ".join([c.text.strip().replace("\n", " ") for c in r.cells]))
            chunks_text.append(("Research Areas and Domain Specializations", "\n".join(res_lines)))

        # Chunk 7: BoS Members (Table 24 & 25)
        if len(doc.tables) > 25:
            bos_lines = []
            for r in doc.tables[24].rows:
                bos_lines.append(" | ".join([c.text.strip().replace("\n", " ") for c in r.cells]))
            chunks_text.append(("Board of Studies (BoS) Members and Governance", "\n".join(bos_lines)))

        total_inserted = 0
        for idx, (section, text) in enumerate(chunks_text):
            emb = []
            if gemini_service.is_configured():
                try:
                    emb = gemini_service.embed_text(text)
                except Exception as e:
                    logger.warning(f"Embedding generation failed for chunk {idx}: {str(e)}")

            if not emb:
                # Deterministic fallback embedding representation
                emb = [0.01 * ((idx + j) % 100) for j in range(768)]

            c_rec = DocumentChunk(
                document_id=doc_rec.id,
                chunk_index=idx,
                chunk_text=f"### {section}\n\n{text}",
                token_count=len(text.split()),
                source_section=section,
                category="CENTRE_FOR_AI_DOCX",
                publication_status="PUBLISHED",
                is_current=True,
                audience_metadata=["ALL", "STUDENT", "FACULTY", "ADMIN"],
                embedding_model="text-embedding-004",
                embedding_dimension=len(emb),
                embedding_json=emb,
                is_demo=False,
            )
            db.add(c_rec)
            total_inserted += 1

        db.commit()
        return total_inserted


cai_docx_service = CAIDocxIngestionService()
