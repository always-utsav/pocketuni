from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class Skill(Base, CommonMixin):
    __tablename__ = "skills"

    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)  # Frontend, Backend, AI/ML, Mobile, etc.


class StudentProfile(Base, CommonMixin):
    __tablename__ = "student_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Institution-controlled fields (Read-only for student, editable only by Super Admin)
    enrolment_number = Column(String(50), nullable=True, index=True)
    programme = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)
    batch = Column(String(50), nullable=True)
    semester = Column(Integer, nullable=True)
    section = Column(String(20), nullable=True)
    academic_year = Column(String(50), nullable=True)
    date_of_admission = Column(String(50), nullable=True)
    data_source = Column(String(100), default="official", nullable=False)

    # User-editable student fields
    bio = Column(Text, nullable=True)
    looking_for = Column(Text, nullable=True)
    open_for_hackathons = Column(Boolean, default=True, nullable=False)
    open_source_contributor = Column(Boolean, default=False, nullable=False)
    competitive_programming = Column(Boolean, default=False, nullable=False)
    competitive_handles = Column(JSON, default=dict, nullable=False)
    github_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    resume_url = Column(String(500), nullable=True)
    achievements = Column(JSON, default=list, nullable=False)
    certifications = Column(JSON, default=list, nullable=False)
    experience = Column(JSON, default=list, nullable=False)
    availability_hours_per_week = Column(Integer, default=15, nullable=False)
    availability_notes = Column(Text, nullable=True)
    preferred_roles = Column(JSON, default=list, nullable=False)
    clubs = Column(JSON, default=list, nullable=False)
    tech_stack = Column(JSON, default=list, nullable=False)
    interests = Column(JSON, default=list, nullable=False)
    domains = Column(JSON, default=list, nullable=False)
    completeness_score = Column(Integer, default=70, nullable=False)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    skills = relationship("StudentSkill", back_populates="student_profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="student_profile", cascade="all, delete-orphan")
    resume_metadata = relationship("ResumeMetadata", back_populates="student_profile", uselist=False, cascade="all, delete-orphan")
    visibility = relationship("ProfileVisibility", back_populates="student_profile", uselist=False, cascade="all, delete-orphan")


class StudentSkill(Base, CommonMixin):
    __tablename__ = "student_skills"

    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    proficiency = Column(String(50), default="Intermediate", nullable=False)  # Beginner, Intermediate, Advanced
    category = Column(String(50), nullable=True)

    student_profile = relationship("StudentProfile", back_populates="skills")


class Project(Base, CommonMixin):
    __tablename__ = "projects"

    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    repo_url = Column(String(255), nullable=True)
    live_url = Column(String(255), nullable=True)
    tech_notes = Column(JSON, default=list, nullable=False)

    student_profile = relationship("StudentProfile", back_populates="projects")


class ResumeMetadata(Base, CommonMixin):
    __tablename__ = "resume_metadata"

    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    content_hash = Column(String(64), nullable=False)
    uploaded_at = Column(String(50), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="resume_metadata")


class ProfileVisibility(Base, CommonMixin):
    __tablename__ = "profile_visibility"

    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    is_public = Column(Boolean, default=True, nullable=False)
    show_contact = Column(Boolean, default=False, nullable=False)
    show_cgpa = Column(Boolean, default=False, nullable=False)  # Private by default

    student_profile = relationship("StudentProfile", back_populates="visibility")
