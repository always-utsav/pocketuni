from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class FacultyProfile(Base, CommonMixin):
    __tablename__ = "faculty_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    
    # Institution-controlled fields
    faculty_identifier = Column(String(50), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    designation = Column(String(100), nullable=False)
    department = Column(String(150), nullable=False, index=True)
    centre = Column(String(150), nullable=True)
    qualification = Column(String(255), nullable=True)
    official_profile_url = Column(String(500), nullable=True)
    courses = Column(JSON, default=list, nullable=False)
    data_source = Column(String(100), default="official", nullable=False)
    
    # User-editable faculty fields
    bio = Column(Text, nullable=True)
    office_location = Column(String(255), nullable=True)
    office_hours = Column(String(255), nullable=True)
    email_public = Column(String(255), nullable=True)
    phone_public = Column(String(50), nullable=True)
    photo_url = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    content_hash = Column(String(64), nullable=True)
    areas_of_expertise = Column(JSON, default=list, nullable=False)
    projects_json = Column(JSON, default=list, nullable=False)
    publications_json = Column(JSON, default=list, nullable=False)
    professional_highlights_json = Column(JSON, default=list, nullable=False)
    external_links_json = Column(JSON, default=dict, nullable=False)
    phone_internal = Column(String(50), nullable=True)
    verification_status = Column(
        String(50), default="VERIFIED_OFFICIAL_SOURCE", nullable=False
    )  # VERIFIED_OFFICIAL_SOURCE, NEEDS_REVIEW, SOURCE_UNAVAILABLE, HISTORICAL_INFORMATION
    is_mentor = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="faculty_profile")
    research_interests = relationship("FacultyResearchInterest", back_populates="faculty_profile", cascade="all, delete-orphan")
    education = relationship("FacultyEducation", back_populates="faculty_profile", cascade="all, delete-orphan")
    experience = relationship("FacultyExperience", back_populates="faculty_profile", cascade="all, delete-orphan")
    publications = relationship("FacultyPublication", back_populates="faculty_profile", cascade="all, delete-orphan")
    source = relationship("FacultySource", back_populates="faculty_profile", uselist=False, cascade="all, delete-orphan")


class FacultyResearchInterest(Base, CommonMixin):
    __tablename__ = "faculty_research_interests"

    faculty_profile_id = Column(String(36), ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    area = Column(String(255), nullable=False)

    faculty_profile = relationship("FacultyProfile", back_populates="research_interests")


class FacultyEducation(Base, CommonMixin):
    __tablename__ = "faculty_education"

    faculty_profile_id = Column(String(36), ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    degree = Column(String(100), nullable=False)
    institution = Column(String(255), nullable=False)
    year = Column(Integer, nullable=True)

    faculty_profile = relationship("FacultyProfile", back_populates="education")


class FacultyExperience(Base, CommonMixin):
    __tablename__ = "faculty_experience"

    faculty_profile_id = Column(String(36), ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(String(100), nullable=False)
    organization = Column(String(255), nullable=False)
    duration = Column(String(100), nullable=True)

    faculty_profile = relationship("FacultyProfile", back_populates="experience")


class FacultyPublication(Base, CommonMixin):
    __tablename__ = "faculty_publications"

    faculty_profile_id = Column(String(36), ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    journal = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    doi = Column(String(150), nullable=True)

    faculty_profile = relationship("FacultyProfile", back_populates="publications")


class FacultySource(Base, CommonMixin):
    __tablename__ = "faculty_sources"

    faculty_profile_id = Column(String(36), ForeignKey("faculty_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    source_url = Column(String(500), nullable=False)
    retrieved_at = Column(DateTime(timezone=True), nullable=False)
    raw_html_snapshot = Column(Text, nullable=True)

    faculty_profile = relationship("FacultyProfile", back_populates="source")
