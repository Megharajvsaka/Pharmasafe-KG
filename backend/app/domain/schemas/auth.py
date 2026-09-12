"""
auth.py
-------
Pydantic schemas for User authentication and registration.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="Institutional or academic email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure user password (min 8 chars)")
    full_name: str = Field(..., min_length=2, max_length=150, description="Full name of researcher or clinician")
    role: str = Field(default="researcher", description="Account role: clinician, researcher, or student")
    institution: Optional[str] = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Invalid email format.")
        return clean

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if v.isdigit() or v.isalpha():
            raise ValueError("Password should contain a mix of letters, numbers, or special characters.")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        clean = v.strip().lower()
        allowed = {"admin", "clinician", "researcher", "student", "faculty"}
        if clean not in allowed:
            return "researcher"
        return clean


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: str
    institution: Optional[str] = None
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
    status: str = "ok"
