import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from docx import Document
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.identity import User
from backend.app.models.student import StudentProfile
from backend.app.models.application import Application, ApplicationVersionModel, ApplicationStatusHistory
from backend.app.services.gemini_service import gemini_service

logger = logging.getLogger("pocketuni.application_agent")

SLOT_EXTRACTION_PROMPT = """You are the PocketUni Conversational Application Agent for MITS Gwalior.
Your role is to help university students generate formal academic applications (Leave, Bonafide, NOC, Permission, Fee Concession, etc.).

Analyze the conversation and extract key application parameters into a strict JSON object:
{
    "type": "leave" | "bonafide" | "permission" | "noc" | "fee" | "general",
    "recipient_title": "Head of Department" | "Dean of Academic Affairs" | "Director" | "Faculty Advisor" | null,
    "recipient_department": string | null,
    "start_date": string | null,
    "end_date": string | null,
    "duration_days": string | null,
    "reason": string | null,
    "missing_fields": ["start_date", "reason", "recipient_title", ...] // list of missing critical fields needed before generating application
}

Rules:
- If critical details are missing (e.g. dates/reason for leave; purpose for NOC; dates for permission), list them in "missing_fields".
- Only respond with valid raw JSON. No markdown ticks, no preamble.
"""

class ApplicationAgentService:

    def process_message(
        self,
        db: Session,
        student_user: User,
        user_message: str,
        conversation_history: list,
        current_slots: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processes a conversational message from a student, gathering required parameters
        or generating a formal application draft once all parameters are present.
        """
        student_info = {
            "name": student_user.full_name or "Student",
            "email": student_user.email,
            "roll_number": student_user.roll_number or "N/A",
            "branch": student_user.branch or "Artificial Intelligence & Data Science",
            "semester": student_user.year_of_study or "4th Semester",
            "academic_year": "2026-27"
        }

        # Analyze message with Gemini to extract slots
        conv_summary = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in conversation_history[-4:]])
        prompt = (
            f"Existing known parameters: {json.dumps(current_slots or {})}\n"
            f"Recent history:\n{conv_summary}\n"
            f"Latest student message: {user_message}\n"
            f"Extract parameters JSON:"
        )

        slots = current_slots or {}
        try:
            gemini_res = gemini_service.generate_content(
                prompt=prompt,
                system_instruction=SLOT_EXTRACTION_PROMPT,
                temperature=0.1
            ).strip()
            # Clean possible markdown block
            if gemini_res.startswith("```"):
                gemini_res = gemini_res.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            extracted = json.loads(gemini_res)
            # Merge slots
            for k, v in extracted.items():
                if v is not None:
                    slots[k] = v
        except Exception as e:
            logger.warning(f"Slot extraction fallback used: {e}")
            if not slots.get("type"):
                slots["type"] = "general"

        missing = slots.get("missing_fields", [])

        # If details are still missing, formulate a polite conversational inquiry
        if missing and ("dates" in str(missing) or "reason" in str(missing) or "start_date" in str(missing)):
            inquiry_prompt = (
                f"You are the PocketUni Application Agent. The student wants to create a {slots.get('type', 'general')} application. "
                f"The following details are still needed: {', '.join(missing)}. "
                f"Respond with a polite, brief, helpful sentence asking the student to provide the missing details."
            )
            reply = gemini_service.generate_content(prompt=inquiry_prompt, temperature=0.3)
            return {
                "reply": reply,
                "slots": slots,
                "is_draft_ready": False,
                "application_id": None
            }

        # All necessary parameters collected: Generate the formal application draft
        draft_text = self._synthesize_application_text(slots, student_info)
        app_title = f"{slots.get('type', 'General').capitalize()} Application - {student_info['name']}"

        # Persist or update Application in DB
        app_record = Application(
            student_id=student_user.id,
            title=app_title,
            type=slots.get("type", "general"),
            status="draft",
            current_version_no=1,
            content=draft_text
        )
        db.add(app_record)
        db.flush()

        # Add initial version
        db.add(ApplicationVersionModel(
            application_id=app_record.id,
            version_no=1,
            content=draft_text,
            created_by_role="ai"
        ))

        # Add status history
        db.add(ApplicationStatusHistory(
            application_id=app_record.id,
            from_status="created",
            to_status="draft",
            actor_user_id=student_user.id,
            actor_name=student_info["name"],
            note="Application draft generated by AI agent"
        ))

        # Generate DOCX document
        self.generate_docx(app_record.id, draft_text, app_title)

        db.commit()

        return {
            "reply": f"I have drafted your formal **{app_title}** based on your verified student profile. You can review the draft below, make manual edits if needed, or submit it to your faculty advisor.",
            "slots": slots,
            "is_draft_ready": True,
            "application_id": app_record.id,
            "draft_content": draft_text
        }

    def _synthesize_application_text(self, slots: Dict[str, Any], student: Dict[str, Any]) -> str:
        app_type = slots.get("type", "general")
        recipient = slots.get("recipient_title") or "The Head of Department"
        dept = slots.get("recipient_department") or "Centre for Artificial Intelligence"
        reason = slots.get("reason") or "personal reasons"
        dates = ""
        if slots.get("start_date") and slots.get("end_date"):
            dates = f"from {slots['start_date']} to {slots['end_date']}"
        elif slots.get("duration_days"):
            dates = f"for a duration of {slots['duration_days']}"
        else:
            dates = "for the upcoming scheduled dates"

        subject = f"Application for {app_type.replace('_', ' ').capitalize()} - Reg."
        if app_type == "leave":
            subject = f"Application for leave of absence {dates}"
        elif app_type == "bonafide":
            subject = "Request for Issuance of Bonafide Certificate"
        elif app_type == "noc":
            subject = "Request for No Objection Certificate (NOC) for Internship"

        body = (
            f"Respected Sir/Madam,\n\n"
            f"I am writing to formally request approval for {app_type.replace('_', ' ')} {dates} on account of {reason}.\n\n"
            f"I assure you that I will cover all missed coursework, lecture notes, and lab assignments promptly upon my return, and will maintain compliance with the departmental attendance standards.\n\n"
            f"Kindly consider my request and grant the necessary permission."
        )

        return (
            f"To,\n"
            f"{recipient},\n"
            f"{dept},\n"
            f"Madhav Institute of Technology & Science (MITS),\n"
            f"Gwalior, Madhya Pradesh.\n\n"
            f"Date: {datetime.now().strftime('%d %B, %Y')}\n\n"
            f"Subject: {subject}\n\n"
            f"{body}\n\n"
            f"Thanking you,\n\n"
            f"Yours faithfully,\n"
            f"Name: {student['name']}\n"
            f"Enrollment / Roll No: {student['roll_number']}\n"
            f"Branch / Programme: {student['branch']}\n"
            f"Current Semester: Semester {student['semester']}\n"
            f"Academic Session: {student['academic_year']}\n"
            f"Email: {student['email']}"
        )

    def generate_docx(self, application_id: str, content: str, title: str) -> str:
        """Generates formal Word document and returns storage path."""
        doc = Document()
        doc.add_heading(title, level=1)
        for paragraph in content.split("\n\n"):
            if paragraph.strip():
                doc.add_paragraph(paragraph.strip())

        output_dir = os.path.join(settings.STORAGE_DIR, "application_documents")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{application_id}.docx")
        doc.save(file_path)
        return file_path


application_agent_service = ApplicationAgentService()
