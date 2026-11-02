from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class Institution(Base, CommonMixin):
    __tablename__ = "institutions"

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    website_url = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)

    departments = relationship("Department", back_populates="institution", cascade="all, delete-orphan")


class Department(Base, CommonMixin):
    __tablename__ = "departments"

    institution_id = Column(String(36), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    overview = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    head_of_department = Column(String(255), nullable=True)

    institution = relationship("Institution", back_populates="departments")
    programmes = relationship("Programme", back_populates="department", cascade="all, delete-orphan")


class Programme(Base, CommonMixin):
    __tablename__ = "programmes"

    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    degree = Column(String(50), nullable=False)  # B.Tech, M.Tech, Ph.D.
    duration_years = Column(Integer, default=4, nullable=False)
    description = Column(Text, nullable=True)

    department = relationship("Department", back_populates="programmes")
    branches = relationship("Branch", back_populates="programme", cascade="all, delete-orphan")


class Branch(Base, CommonMixin):
    __tablename__ = "branches"

    programme_id = Column(String(36), ForeignKey("programmes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)

    programme = relationship("Programme", back_populates="branches")


class AcademicYear(Base, CommonMixin):
    __tablename__ = "academic_years"

    year_label = Column(String(50), unique=True, nullable=False, index=True)  # e.g., '2026-2027'
    is_current = Column(Integer, default=0, nullable=False)


class Semester(Base, CommonMixin):
    __tablename__ = "semesters"

    semester_number = Column(Integer, nullable=False)
    academic_year_id = Column(String(36), ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False, index=True)
    term_type = Column(String(20), nullable=False)  # 'Autumn' / 'Spring' or 'Odd' / 'Even'


class Batch(Base, CommonMixin):
    __tablename__ = "batches"

    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    graduation_year = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)


class Laboratory(Base, CommonMixin):
    __tablename__ = "laboratories"

    data_source = Column(String(50), default="official", nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    location = Column(String(100), nullable=True)
    capacity = Column(Integer, default=30, nullable=False)
    hardware_specs = Column(Text, nullable=True)
    software_specs = Column(Text, nullable=True)
    faculty_in_charge = Column(String(255), nullable=True)
    staff_in_charge = Column(String(255), nullable=True)
    research_focus = Column(Text, nullable=True)
    description = Column(Text, nullable=True)


class DepartmentProgramme(Base, CommonMixin):
    __tablename__ = "department_programmes"

    data_source = Column(String(50), default="official", nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    degree = Column(String(50), nullable=False)  # B.Tech, M.Tech, Ph.D.
    intake = Column(Integer, default=60, nullable=False)
    duration_years = Column(Integer, default=4, nullable=False)
    curriculum_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)


class BoSMember(Base, CommonMixin):
    __tablename__ = "bos_members"

    data_source = Column(String(50), default="official", nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    designation = Column(String(255), nullable=True)
    affiliation = Column(String(255), nullable=True)
    category = Column(String(100), nullable=False)  # Chairman, Internal, External, Industry, Alumni
    email = Column(String(255), nullable=True)


class DepartmentEvent(Base, CommonMixin):
    __tablename__ = "department_events"

    data_source = Column(String(50), default="official", nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # Workshop, FDP, Expert Talk, Seminar
    date_start = Column(String(50), nullable=True)
    date_end = Column(String(50), nullable=True)
    coordinator = Column(String(255), nullable=True)
    speaker = Column(String(255), nullable=True)
    brochure_url = Column(String(500), nullable=True)
    report_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)


class ClassCoordinator(Base, CommonMixin):
    __tablename__ = "class_coordinators"

    data_source = Column(String(50), default="official", nullable=False)
    year = Column(String(50), nullable=False, index=True)  # I Year, II Year, III Year, IV Year
    branch = Column(String(100), nullable=False, index=True)  # AIR, AIML, AIDS, AI
    faculty_name = Column(String(255), nullable=False, index=True)
    contact_number = Column(String(50), nullable=True)
    institutional_email = Column(String(255), nullable=True)
    academic_session = Column(String(50), default="2026-2027", nullable=False)


class ConflictReview(Base, CommonMixin):
    __tablename__ = "conflict_reviews"

    data_source = Column(String(50), default="official", nullable=False)
    source_document = Column(String(255), nullable=False)
    field_name = Column(String(100), nullable=False)
    source_content = Column(Text, nullable=False)
    conflict_description = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, RESOLVED
    resolution_notes = Column(Text, nullable=True)

