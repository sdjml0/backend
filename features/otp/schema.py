from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class SendMagicLinkRequest(BaseModel):
    email: EmailStr
    purpose: Optional[Literal["signup", "password_reset"]] = None


SendOTPRequest = SendMagicLinkRequest


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    purpose: Optional[Literal["signup", "password_reset"]] = "password_reset"


class MagicLinkResponse(BaseModel):
    success: bool = True
    message: str
    expires_in_minutes: int = 10


OTPResponse = MagicLinkResponse


class ResetPasswordRequest(BaseModel):
    token: Optional[str] = Field(None, description="Long alphanumeric magic link token from email URL")
    resetotp: Optional[str] = Field(None, description="Alias for token")
    otp: Optional[str] = Field(None, description="Alias for token")
    code: Optional[str] = Field(None, description="Alias for token")

    new_password: Optional[str] = Field(None, description="New password minimum 6 chars")
    password: Optional[str] = Field(None, description="Alias for new_password")
    newPassword: Optional[str] = Field(None, description="Alias for new_password")

    email: Optional[EmailStr] = None

    def get_token(self) -> Optional[str]:
        return self.token or self.resetotp or self.otp or self.code

    def get_password(self) -> Optional[str]:
        return self.new_password or self.password or self.newPassword


class VerifyLinkResponse(BaseModel):
    success: bool = True
    message: str
    purpose: str
    email: str
    accessToken: Optional[str] = None
    expiresIn: Optional[int] = None
    user: Optional[dict] = None


