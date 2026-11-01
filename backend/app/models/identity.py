from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import CommonMixin


class Role(Base, CommonMixin):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)  # SUPER_ADMIN, FACULTY, STUDENT
    description = Column(String(255), nullable=True)

    users = relationship("UserRole", back_populates="role")


class User(Base, CommonMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    picture_url = Column(Text, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    google_sub = Column(String(255), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Specific attributes
    roll_number = Column(String(50), nullable=True, index=True)
    branch = Column(String(100), nullable=True)
    year_of_study = Column(String(20), nullable=True)
    department_name = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)

    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    faculty_profile = relationship("FacultyProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    auth_accounts = relationship("AuthenticationAccount", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", foreign_keys="Application.student_id")
    assigned_applications = relationship("Application", back_populates="faculty", foreign_keys="Application.faculty_id")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class UserRole(Base, CommonMixin):
    __tablename__ = "user_roles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


class AuthenticationAccount(Base, CommonMixin):
    __tablename__ = "authentication_accounts"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # 'google', 'local_dev'
    provider_user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)

    user = relationship("User", back_populates="auth_accounts")


class UserSession(Base, CommonMixin):
    __tablename__ = "user_sessions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)

    user = relationship("User", back_populates="sessions")
