from typing import List
from sqlalchemy.orm import Session
from backend.app.models.identity import User
from backend.app.models.document import InstitutionalDocument, DocumentAudience


class AudienceEnforcementService:
    def can_user_access_document(self, user: User, document: InstitutionalDocument) -> bool:
        # SUPER_ADMIN can access everything
        user_roles = [r.role.name for r in user.roles if r.role] if hasattr(user, 'roles') and user.roles else []
        if "SUPER_ADMIN" in user_roles:
            return True

        # Non-published documents cannot be accessed by non-admins
        if document.status != "PUBLISHED" or not document.is_current_published:
            return False

        audiences = document.audiences
        if not audiences:
            # If no audience configured, default to institution-wide published
            return True

        is_student = "STUDENT" in user_roles
        is_faculty = "FACULTY" in user_roles

        for aud in audiences:
            st = aud.scope_type.upper()
            val = (aud.scope_value or "").lower()

            if st == "ENTIRE_INSTITUTION":
                return True
            
            if st == "STUDENTS_ONLY" and is_student:
                return True
                
            if st == "FACULTY_ONLY" and is_faculty:
                return True

            if st == "CENTRE_FOR_AI":
                user_branch = (user.branch or "").lower()
                user_dept = (user.department_name or "").lower()
                if "ai" in user_branch or "artificial intelligence" in user_branch or "ai" in user_dept:
                    return True

            if st == "BRANCH" and user.branch:
                if val in user.branch.lower():
                    return True

            if st == "DEPARTMENT" and user.department_name:
                if val in user.department_name.lower():
                    return True

            if st == "SEMESTER" and is_student and user.year_of_study:
                # Approximate year of study to semester
                if val in str(user.year_of_study).lower():
                    return True

            if st == "SPECIFIC_USERS" and aud.scope_value == user.id:
                return True

        return False


audience_service = AudienceEnforcementService()
