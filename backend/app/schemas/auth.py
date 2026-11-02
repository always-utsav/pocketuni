from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    email: str
    full_name: str
    picture_url: Optional[str] = None
    active_context: Optional[str] = None
    user: Optional[dict] = None


class TokenPayload(BaseModel):
    sub: str
    role: str
    email: str
    active_context: Optional[str] = None
    exp: Optional[int] = None


class LocalDevLoginRequest(BaseModel):
    email: str


class CurrentUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    active_context: Optional[str] = None
    picture_url: Optional[str] = None
    roll_number: Optional[str] = None
    branch: Optional[str] = None
    year_of_study: Optional[str] = None
    department_name: Optional[str] = None
    designation: Optional[str] = None
    is_active: bool
    is_demo: bool
