from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token
from backend.app.core.permissions import get_current_user
from backend.app.models.identity import User, Role, UserRole
from backend.app.schemas.auth import (
    Token,
    LocalDevLoginRequest,
    CurrentUserResponse,
)
from backend.app.services.audit_service import log_audit_event

router = APIRouter()


@router.get("/demo-accounts")
def get_demo_accounts():
    """Return available demo personas for local development authentication."""
    return [
        {
            "email": "utsavkumawat05@gmail.com",
            "name": "Utsav Kumawat",
            "role": "SUPER_ADMIN",
            "subtitle": "Institutional Super Administrator",
            "badge": "Super Admin",
            "pictureUrl": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80",
            "is_demo": True
        },
        {
            "email": "aarav.sharma@example.invalid",
            "name": "Aarav Sharma",
            "role": "STUDENT",
            "subtitle": "B.Tech IT (AI & Robotics) — 2nd Year",
            "badge": "Student (2nd Yr)",
            "pictureUrl": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80",
            "is_demo": True
        },
        {
            "email": "mahi.gupta@example.invalid",
            "name": "Mahi Gupta",
            "role": "STUDENT",
            "subtitle": "B.Tech Artificial Intelligence — 3rd Year",
            "badge": "Student (3rd Yr)",
            "pictureUrl": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80",
            "is_demo": True
        },
        {
            "email": "ankur.yadav@example.invalid",
            "name": "Ankur Singh Yadav",
            "role": "STUDENT",
            "subtitle": "B.Tech AI & Machine Learning — 3rd Year",
            "badge": "Student (3rd Yr)",
            "pictureUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            "is_demo": True
        },
        {
            "email": "mahi.choudhary@example.invalid",
            "name": "Mahi Choudhary",
            "role": "STUDENT",
            "subtitle": "B.Tech AI & Data Science — 2nd Year",
            "badge": "Student (2nd Yr)",
            "pictureUrl": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            "is_demo": True
        },
        {
            "email": "dr.mausam.chouksey@mitsgwalior.in",
            "name": "Dr. Mausam Chouksey",
            "role": "FACULTY",
            "subtitle": "Assistant Professor, CAI & ECE (Designated Mentor)",
            "badge": "Faculty (Mentor)",
            "pictureUrl": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
            "is_demo": False
        },
        {
            "email": "rajni.makwana@mitsgwalior.in",
            "name": "Dr. Rajni Ranjan Singh Makwana",
            "role": "FACULTY",
            "subtitle": "Associate Professor & Head / Dean, CAI",
            "badge": "Faculty (Head CAI)",
            "pictureUrl": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            "is_demo": False
        }
    ]


@router.post("/dev-login", response_model=Token)
@router.get("/dev-login", response_model=Token)
def local_dev_login(
    payload: Optional[LocalDevLoginRequest] = None,
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Controlled local development login supporting both POST and GET.
    Enforces super admin allowlist and assigns verified roles.
    Disabled in production configuration.
    """
    if not settings.LOCAL_DEV_AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development login mode is disabled in this environment."
        )

    target_email = (payload.email if payload else email or "").strip().lower()
    if not target_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address must be provided in request body or query parameter."
        )

    # Query user from DB
    user = db.query(User).filter(User.email == target_email, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with email '{target_email}' is not pre-registered in PocketUni database."
        )

    # Determine highest role
    user_roles = [ur.role.name for ur in user.roles if ur.role]
    primary_role = "STUDENT"
    if "SUPER_ADMIN" in user_roles:
        primary_role = "SUPER_ADMIN"
    elif "FACULTY" in user_roles:
        primary_role = "FACULTY"

    # Super admin allowlist check
    if primary_role == "SUPER_ADMIN" and target_email not in [e.lower() for e in settings.SUPER_ADMIN_ALLOWLIST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not in the configured Super Admin allowlist."
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    # Log audit event
    log_audit_event(
        db=db,
        actor_email=user.email,
        actor_role=primary_role,
        action="DEV_LOGIN_SUCCESS",
        target_entity="User",
        target_id=user.id,
        change_summary=f"User signed in via local development login mode with role {primary_role}.",
        actor_user_id=user.id
    )

    access_token = create_access_token(
        subject=user.id,
        role=primary_role,
        email=user.email
    )

    return Token(
        access_token=access_token,
        role=primary_role,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        picture_url=user.picture_url
    )


class SandboxLoginRequest(BaseModel):
    role: str  # SUPER_ADMIN, STUDENT, FACULTY


@router.post("/sandbox-login", response_model=Token)
@router.get("/sandbox-login", response_model=Token)
def sandbox_login(
    payload: Optional[SandboxLoginRequest] = None,
    role: Optional[str] = Query(None),
    persona: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Authenticates into one of the three designated sandbox identities:
    - SUPER_ADMIN: Institutional Super Administrator
    - STUDENT: B.Tech AIR Student
    - FACULTY: CAI Faculty Member & Mentor
    Uses stable pre-existing IDs without creating duplicate accounts.
    """
    req_role = (payload.role if payload else role or persona or "STUDENT").strip().upper()

    if req_role in ["SUPER_ADMIN", "ADMIN"]:
        email = "utsavkumawat05@gmail.com"
        target_role = "SUPER_ADMIN"
    elif req_role in ["FACULTY", "MENTOR"]:
        email = "dr.mausam.chouksey@mitsgwalior.in"
        target_role = "FACULTY"
    elif req_role in ["STUDENT"]:
        email = "aarav.sharma@example.invalid"
        target_role = "STUDENT"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sandbox role '{req_role}'. Supported roles: SUPER_ADMIN, FACULTY, STUDENT."
        )

    user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Sandbox account for role '{target_role}' not found.")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    log_audit_event(
        db=db,
        actor_email=user.email,
        actor_role=target_role,
        action="SANDBOX_LOGIN",
        target_entity="User",
        target_id=user.id,
        change_summary=f"Signed in as {target_role} Sandbox identity.",
        actor_user_id=user.id
    )

    access_token = create_access_token(
        subject=user.id,
        role=target_role,
        email=user.email
    )

    return Token(
        access_token=access_token,
        role=target_role,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        picture_url=user.picture_url,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": target_role,
            "picture_url": user.picture_url,
            "branch": user.branch,
            "department_name": user.department_name,
            "designation": user.designation,
            "year_of_study": user.year_of_study
        }
    )


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    primary_role = "STUDENT"
    if "SUPER_ADMIN" in user_roles:
        primary_role = "SUPER_ADMIN"
    elif "FACULTY" in user_roles:
        primary_role = "FACULTY"

    active_context = getattr(current_user, "_active_context", None) or primary_role

    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=primary_role,
        active_context=active_context,
        picture_url=current_user.picture_url,
        roll_number=current_user.roll_number,
        branch=current_user.branch,
        year_of_study=current_user.year_of_study,
        department_name=current_user.department_name,
        designation=current_user.designation,
        is_active=current_user.is_active,
        is_demo=current_user.is_demo
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    primary_role = user_roles[0] if user_roles else "STUDENT"
    log_audit_event(
        db=db,
        actor_email=current_user.email,
        actor_role=primary_role,
        action="LOGOUT",
        target_entity="User",
        target_id=current_user.id,
        change_summary="User logged out.",
        actor_user_id=current_user.id
    )
    return {"message": "Successfully logged out."}


@router.get("/oauth-status")
def get_oauth_status():
    from backend.app.services.oauth_service import google_oauth_service
    return {
        "configured": google_oauth_service.is_configured(),
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }


@router.get("/google/url")
def get_google_oauth_url(role: str = "STUDENT"):
    from backend.app.services.oauth_service import google_oauth_service
    try:
        url, state = google_oauth_service.generate_authorization_url(intended_role=role)
        return {"url": url, "state": state, "role": role}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str


@router.get("/google/callback")
async def google_oauth_callback_get(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Handles browser redirects from Google OAuth consent screen (GET request).
    Exchanges code for tokens and redirects cleanly to frontend with authorization token.
    """
    from fastapi.responses import RedirectResponse
    from backend.app.services.oauth_service import google_oauth_service
    frontend_url = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"

    if not code or not state:
        return RedirectResponse(url=f"{frontend_url}/?error=Missing+OAuth+code+or+state")

    try:
        ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        res = await google_oauth_service.handle_callback(
            db=db,
            code=code,
            state=state,
            ip_address=ip,
            user_agent=user_agent
        )
        token = res.get("access_token")
        role = res.get("role", "STUDENT")
        return RedirectResponse(url=f"{frontend_url}/?token={token}&role={role}")
    except Exception as e:
        logger.error(f"Google OAuth callback GET failed: {e}")
        return RedirectResponse(url=f"{frontend_url}/?error={str(e)}")


@router.post("/google/callback")
async def google_oauth_callback(
    payload: GoogleCallbackRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    from backend.app.services.oauth_service import google_oauth_service
    try:
        ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        res = await google_oauth_service.handle_callback(
            db=db,
            code=payload.code,
            state=payload.state,
            ip_address=ip,
            user_agent=user_agent
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ContextSwitchRequest(BaseModel):
    target_context: str


@router.post("/context-switch")
def switch_admin_context(
    payload: ContextSwitchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from backend.app.services.oauth_service import google_oauth_service
    try:
        return google_oauth_service.switch_context(db, current_user, payload.target_context)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
