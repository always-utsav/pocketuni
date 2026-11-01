import re
from typing import Dict, Any, List


class DocumentClassificationService:
    # 16 standard categories defined in Part E
    CATEGORIES = [
        "TIMETABLE",
        "SCHEME_OF_STUDY",
        "SYLLABUS",
        "INDUCTION_NOTICE",
        "GENERAL_NOTICE",
        "EXAMINATION_DATESHEET",
        "INTERNAL_MARKS",
        "FINAL_RESULTS",
        "ACADEMIC_CALENDAR",
        "PROFESSIONAL_CERTIFICATION_LIST",
        "COURSE_STRUCTURE",
        "LAB_MANUAL",
        "ACADEMIC_POLICY",
        "FACULTY_DOCUMENT",
        "GENERAL_INSTITUTIONAL_DOCUMENT",
        "OTHER",
    ]

    def classify_and_extract_metadata(
        self,
        title: str,
        contents: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
        source_filename: str = ""
    ) -> Dict[str, Any]:
        combined_text = " ".join([c.get("content", "") for c in contents[:200]])
        full_text_lower = f"{title.lower()} {source_filename.lower()} {combined_text.lower()}"

        # 1. Determine Category
        category = "OTHER"
        confidence = "LOW"

        if re.search(r'\b(minor\s*(?:evaluation|eval)?[\s\-_]*[0-9]*\s*marks|theory\s*(?:and|&)\s*lab(?:oratory)?\s*marks|internal\s*marks|class\s*test\s*marks)\b', full_text_lower):
            category = "INTERNAL_MARKS"
            confidence = "HIGH"
        elif re.search(r'\b(master\s*time\s*table|time\s*table|\btt\b|schedule\s*of\s*classes|class\s*timing)\b', full_text_lower):
            category = "TIMETABLE"
            confidence = "HIGH"
        elif re.search(r'\b(professional\s*certification\s*course\s*list|professional\s*certification\s*platforms|certification\s*course\s*list)\b', full_text_lower):
            category = "PROFESSIONAL_CERTIFICATION_LIST"
            confidence = "HIGH"
        elif re.search(r'\b(induction\s*prog(?:ram(?:me)?)?|first\s*year\s*induction|student\s*induction)\b', full_text_lower):
            category = "INDUCTION_NOTICE"
            confidence = "HIGH"
        elif re.search(r'\b(scheme\s*of\s*study|scheme\s*admitted|teaching\s*and\s*examination\s*scheme)\b', full_text_lower):
            category = "SCHEME_OF_STUDY"
            confidence = "HIGH"
        elif re.search(r'\b(syllabi\s*of\s*all\s*courses|syllabus|course\s*curriculum|course\s*outcomes|course\s*objectives)\b', full_text_lower):
            category = "SYLLABUS"
            confidence = "HIGH"
        elif re.search(r'\b(lab\s*manual|experiment\s*list|list\s*of\s*programs|laboratory\s*manual)\b', full_text_lower):
            category = "LAB_MANUAL"
            confidence = "MEDIUM"
        elif re.search(r'\b(date\s*sheet|examination\s*schedule|exam\s*datesheet)\b', full_text_lower):
            category = "EXAMINATION_DATESHEET"
            confidence = "HIGH"
        elif re.search(r'\b(academic\s*calendar|calendar\s*of\s*events)\b', full_text_lower):
            category = "ACADEMIC_CALENDAR"
            confidence = "HIGH"
        elif re.search(r'\b(final\s*results?|end\s*sem\s*result|tabulation\s*register)\b', full_text_lower):
            category = "FINAL_RESULTS"
            confidence = "HIGH"
        elif re.search(r'\b(course\s*structure|curriculum\s*structure)\b', full_text_lower):
            category = "COURSE_STRUCTURE"
            confidence = "MEDIUM"
        elif re.search(r'\b(academic\s*policy|ordinance|regulations|code\s*of\s*conduct)\b', full_text_lower):
            category = "ACADEMIC_POLICY"
            confidence = "MEDIUM"
        elif re.search(r'\b(faculty\s*profile|faculty\s*directory|faculty\s*document)\b', full_text_lower):
            category = "FACULTY_DOCUMENT"
            confidence = "MEDIUM"
        elif re.search(r'\b(notice|circular|office\s*order)\b', full_text_lower):
            category = "GENERAL_NOTICE"
            confidence = "HIGH"
        elif re.search(r'\b(madhav\s*institute|mits\s*gwalior)\b', full_text_lower):
            category = "GENERAL_INSTITUTIONAL_DOCUMENT"
            confidence = "LOW"

        # 2. Extract Academic Year
        # E.g. 2026-2027, 2025-26, 2024-25, July-Dec 2026
        academic_year = None
        ay_match = re.search(r'\b(202[3-9]\s*[-–/]\s*20?2[4-9])\b', combined_text + " " + source_filename)
        if ay_match:
            ay_raw = ay_match.group(1).replace(" ", "")
            academic_year = ay_raw if len(ay_raw) == 9 else ay_raw[:5] + "20" + ay_raw[5:]
        elif re.search(r'\bjuly\s*[-–]\s*dec\.?\s*2026\b', full_text_lower):
            academic_year = "2026-2027"
        elif re.search(r'\bjan(?:uary)?\s*[-–]\s*june\s*2025\b', full_text_lower):
            academic_year = "2024-2025"

        # 3. Extract Batch
        batch = None
        batch_match = re.search(r'(?:batch\s*admitted\s*in\s*(?:session\s*)?|admitted\s*in\s*session\s*)(202[3-9]\s*[-–/]\s*20?2[4-9])', full_text_lower)
        if batch_match:
            b_raw = batch_match.group(1).replace(" ", "")
            batch = b_raw if len(b_raw) == 7 else b_raw[:5] + b_raw[7:]
        elif re.search(r'2025\s*admitted\s*batch', full_text_lower):
            batch = "2025-26"

        # 4. Extract Semester
        semester = None
        if re.search(r'\b(vii\s*sem(?:ester)?|7th\s*sem(?:ester)?)\b', full_text_lower):
            semester = "VII Semester"
        elif re.search(r'\b(v\s*sem(?:ester)?|5th\s*sem(?:ester)?)\b', full_text_lower):
            semester = "V Semester"
        elif re.search(r'\b(iii\s*sem(?:ester)?|3rd\s*sem(?:ester)?)\b', full_text_lower):
            semester = "III Semester"
        elif re.search(r'\b(ii\s*sem(?:ester)?|2nd\s*sem(?:ester)?)\b', full_text_lower):
            semester = "II Semester"
        elif re.search(r'\b(i\s*sem(?:ester)?|1st\s*sem(?:ester)?|first\s*year)\b', full_text_lower):
            semester = "I Semester"

        # 5. Extract Programme & Branch
        programme = "B.Tech" if re.search(r'\bb\.?\s*tech\b', full_text_lower) else None
        branch = None
        branches_found = []
        if re.search(r'\b(aids|ai\s*&\s*ds|artificial\s*intelligence\s*(?:and|&)\s*data\s*science)\b', full_text_lower):
            branches_found.append("Artificial Intelligence and Data Science")
        if re.search(r'\b(aiml|ai\s*&\s*ml|artificial\s*intelligence\s*(?:and|&)\s*machine\s*learning)\b', full_text_lower):
            branches_found.append("Artificial Intelligence and Machine Learning")
        if re.search(r'\b(air|it\s*\(air\)|artificial\s*intelligence\s*(?:and|&)\s*robotics)\b', full_text_lower):
            branches_found.append("Information Technology (AI and Robotics)")
        if re.search(r'\bb\.?\s*tech\.?\s*iii\s*semester\s*\(artificial\s*intelligence\s*\(ai\)\)', full_text_lower) or re.search(r'\bbranch:\s*artificial\s*intelligence\b', full_text_lower):
            branches_found.append("Artificial Intelligence")
        
        branch = ", ".join(branches_found) if branches_found else "Centre for Artificial Intelligence"

        # 6. Institution & Department
        institution = "Madhav Institute of Technology & Science, Gwalior"
        department = "Centre for Artificial Intelligence"

        # 7. Dates
        effective_date = None
        eff_match = re.search(r'w\.?e\.?f\.?\s*([0-9]{1,2}[\.\-\/][0-9]{1,2}[\.\-\/][0-9]{2,4})', full_text_lower)
        if eff_match:
            effective_date = eff_match.group(1)

        # 8. Privacy & Default Audience
        # Internal marks MUST default to Super Admin only!
        if category == "INTERNAL_MARKS":
            target_roles = ["SUPER_ADMIN"]
            is_sensitive = True
        else:
            target_roles = ["STUDENT", "FACULTY", "SUPER_ADMIN"]
            is_sensitive = False

        return {
            "title": title or source_filename,
            "category": category,
            "confidence": confidence,
            "issuing_institution": institution,
            "department": department,
            "academic_year": academic_year or "2026-2027",
            "batch": batch,
            "programme": programme or "B.Tech",
            "branch": branch,
            "semester": semester,
            "effective_date": effective_date,
            "target_roles": target_roles,
            "is_sensitive": is_sensitive,
            "verification_status": "NEEDS_REVIEW"
        }


classification_service = DocumentClassificationService()
