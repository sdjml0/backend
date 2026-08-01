from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class SendMagicLinkRequest(BaseModel):
    email: EmailStr
    purpose: Literal["signup", "password_reset"] = "signup"


SendOTPRequest = SendMagicLinkRequest


class MagicLinkResponse(BaseModel):
    success: bool = True
    message: str
    expires_in_minutes: int = 10


OTPResponse = MagicLinkResponse


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Long alphanumeric magic link token from email URL")
    new_password: str = Field(..., min_length=6, description="New password minimum 6 chars")


class VerifyLinkResponse(BaseModel):
    success: bool = True
    message: str
    purpose: str
    email: str
    accessToken: Optional[str] = None
    expiresIn: Optional[int] = None
    user: Optional[dict] = None

