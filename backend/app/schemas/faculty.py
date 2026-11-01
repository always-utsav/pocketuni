from typing import List, Optional
from pydantic import BaseModel


class FacultyPublicationSchema(BaseModel):
    title: str
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None


class FacultyProfileOut(BaseModel):
    facultyId: str
    name: str
    designation: str
    department: str
    qualification: Optional[str] = None
    researchAreas: List[str] = []
    publications: List[FacultyPublicationSchema] = []
    emailPublic: Optional[str] = None
    phonePublic: Optional[str] = None
    officeLocation: Optional[str] = None
    officeHours: Optional[str] = None
    photoUrl: Optional[str] = None
    bio: Optional[str] = None
    sourceUrl: Optional[str] = None
    verificationStatus: str
    isMentor: bool = False
    is_demo: bool = False
