import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.identity import User
from backend.app.models.student import StudentProfile, StudentSkill, Project, ProfileVisibility

class DiscoveryEngine:

    def search_collaborators(
        self,
        db: Session,
        query: str,
        current_user: User,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Database-backed student discovery engine.
        Finds matching peers based on real skills, projects, and bio keywords.
        Enforces profile visibility and excludes the requesting student.
        """
        tokens = set(re.findall(r'\w+', query.lower()))
        # Remove common query filler words
        stop_words = {"find", "students", "student", "someone", "interested", "in", "with", "working", "on", "who", "knows", "project", "collaborators", "teammates", "experience", "experienced"}
        search_terms = [t for t in tokens if t not in stop_words and len(t) > 2]
        if not search_terms:
            search_terms = list(tokens)

        # Query all student profiles except the current user
        profiles = db.query(StudentProfile).join(User, StudentProfile.user_id == User.id).filter(
            StudentProfile.user_id != current_user.id,
            User.is_active == True
        ).all()

        matches = []
        for sp in profiles:
            user = sp.user
            # Check visibility settings
            vis = db.query(ProfileVisibility).filter(ProfileVisibility.student_profile_id == sp.id).first()
            if vis and not vis.is_public:
                continue

            matched_tags = set()
            reasons = []

            # 1. Match skills
            skills = [s.skill_name for s in sp.skills]
            for s in sp.skills:
                s_name = s.skill_name.lower()
                for term in search_terms:
                    if term in s_name or s_name in term:
                        matched_tags.add(s.skill_name)
                        reasons.append(f"Has skill: {s.skill_name} ({s.proficiency or 'Proficient'})")

            # 2. Match projects
            for proj in sp.projects:
                proj_text = f"{proj.title} {proj.description or ''} {' '.join(proj.tech_notes or [])}".lower()
                for term in search_terms:
                    if term in proj_text:
                        matched_tags.add(proj.title)
                        reasons.append(f"Worked on project: '{proj.title}'")

            # 3. Match bio and looking_for
            bio_text = f"{sp.bio or ''} {sp.looking_for or ''}".lower()
            for term in search_terms:
                if term in bio_text:
                    reasons.append(f"Mentions '{term}' in interests / looking for")

            score = len(matched_tags) * 2 + len(reasons)
            if score > 0 or not search_terms:
                # Prepare safe, public match card (never expose phone, private email, or marks)
                matches.append({
                    "studentId": user.id,
                    "name": user.full_name or "MITS Student",
                    "email": user.email if (not vis or vis.show_contact) else "Contact via PocketUni",
                    "pictureUrl": user.picture_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.id}",
                    "branch": user.branch or "Artificial Intelligence",
                    "year": int(user.year_of_study) if user.year_of_study and str(user.year_of_study).isdigit() else 3,
                    "rollNumber": user.roll_number,
                    "bio": sp.bio or "MITS AI Student",
                    "matchedTags": list(matched_tags)[:5],
                    "topSkills": skills[:6],
                    "openForHackathons": sp.open_for_hackathons,
                    "matchScore": score,
                    "matchReason": "; ".join(reasons[:2]) if reasons else "Student in matching department",
                    "preferredRoles": sp.preferred_roles or ["Project Collaborator"],
                    "githubUrl": sp.github_url,
                    "linkedinUrl": sp.linkedin_url
                })

        matches.sort(key=lambda x: x["matchScore"], reverse=True)
        return matches[:limit]


discovery_engine = DiscoveryEngine()
