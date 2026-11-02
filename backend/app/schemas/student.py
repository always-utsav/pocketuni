from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class SkillSchema(BaseModel):
    id: Optional[str] = None
    name: str
    proficiency: str = "Intermediate"
    category: Optional[str] = None


class ProjectSchema(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    repoUrl: Optional[str] = None
    liveUrl: Optional[str] = None
    techNotes: List[str] = []


class StudentProfileUpdate(BaseModel):
    bio: Optional[str] = None
    lookingFor: Optional[str] = None
    openForHackathons: Optional[bool] = None
    openSourceContributor: Optional[bool] = None
    competitiveProgramming: Optional[bool] = None
    competitiveHandles: Optional[Dict[str, str]] = None
    githubUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None
    portfolioUrl: Optional[str] = None
    availabilityHoursPerWeek: Optional[int] = None
    availabilityNotes: Optional[str] = None
    preferredRoles: Optional[List[str]] = None
    clubs: Optional[List[str]] = None
    techStack: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    profileVisible: Optional[bool] = None
    skills: Optional[List[SkillSchema]] = None
    projects: Optional[List[ProjectSchema]] = None


class StudentMatchCardSchema(BaseModel):
    studentId: str
    name: str
    email: Optional[str] = None
    pictureUrl: Optional[str] = None
    branch: str
    year: int
    rollNumber: Optional[str] = None
    bio: str
    matchedTags: List[str] = []
    topSkills: List[str] = []
    openForHackathons: bool
    preferredRoles: List[str] = []
    githubUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None
    is_demo: bool = False
