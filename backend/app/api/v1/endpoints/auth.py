"""
auth.py
-------
Authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.domain.models.user import User, RefreshToken, utc_now
from backend.app.core.config import settings
from backend.app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, hash_token
)
from backend.app.domain.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, UserResponse,
    TokenResponse, MessageResponse
)
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

COOKIE_NAME = settings.COOKIE_NAME


def _set_refresh_cookie(response: Response, raw_token: str):
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="lax",
        max_age=max_age,
        path="/auth",
    )


def _clear_refresh_cookie(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/auth")


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, response: Response, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email address is already registered.")

    new_user = User(
        email=email_clean,
        password_hash=hash_password(req.password),
        full_name=req.full_name.strip(),
        role=req.role,
        institution=req.institution.strip() if req.institution else None,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(user_id=new_user.id, email=new_user.email, role=new_user.role)
    raw_refresh, expire_dt = create_refresh_token(user_id=new_user.id)
    db.add(RefreshToken(user_id=new_user.id, token_hash=hash_token(raw_refresh), expires_at=expire_dt))
    db.commit()

    _set_refresh_cookie(response, raw_refresh)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password. Please verify your credentials.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been deactivated.")

    access_token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    raw_refresh, expire_dt = create_refresh_token(user_id=user.id)
    db.add(RefreshToken(user_id=user.id, token_hash=hash_token(raw_refresh), expires_at=expire_dt))
    db.commit()

    _set_refresh_cookie(response, raw_refresh)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_session(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(COOKIE_NAME)
    if not raw_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            raw_token = auth_header.replace("Bearer ", "").strip()

    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh session token provided.")

    try:
        payload = decode_token(raw_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = payload.get("sub")
    except Exception:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or has expired.")

    token_hashed = hash_token(raw_token)
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hashed,
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None)
    ).first()

    if not token_record:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked or is unrecognized.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        token_record.revoked_at = utc_now()
        db.commit()
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive or not found.")

    token_record.revoked_at = utc_now()
    new_raw_refresh, new_expire = create_refresh_token(user_id=user.id)
    db.add(RefreshToken(user_id=user.id, token_hash=hash_token(new_raw_refresh), expires_at=new_expire))
    db.commit()

    _set_refresh_cookie(response, new_raw_refresh)
    return TokenResponse(
        access_token=create_access_token(user_id=user.id, email=user.email, role=user.role),
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(COOKIE_NAME)
    if raw_token:
        token_hashed = hash_token(raw_token)
        rec = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hashed).first()
        if rec and rec.revoked_at is None:
            rec.revoked_at = utc_now()
            db.commit()

    _clear_refresh_cookie(response)
    return MessageResponse(message="Successfully signed out of session.", status="ok")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
