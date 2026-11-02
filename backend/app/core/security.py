from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import jwt
from passlib.context import CryptContext
from backend.app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Optional[Union[str, Any]] = None,
    role: Optional[str] = None,
    email: Optional[str] = None,
    active_context: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
    data: Optional[Dict[str, Any]] = None,
    claims: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {"exp": expire}

    if data:
        to_encode.update(data)
    if claims:
        to_encode.update(claims)
    
    if subject is not None:
        to_encode["sub"] = str(subject)
    if role is not None:
        to_encode["role"] = role
    if email is not None:
        to_encode["email"] = email
    if active_context is not None:
        to_encode["active_context"] = active_context
    elif "active_context" not in to_encode and "role" in to_encode:
        to_encode["active_context"] = to_encode["role"]

    to_encode.update(kwargs)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_payload
    except Exception:
        return None


decode_access_token = decode_token
