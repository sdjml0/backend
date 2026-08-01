from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class SendOTPRequest(BaseModel):
    email: EmailStr
    purpose: Literal["signup", "password_reset"] = "signup"


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit numeric OTP")
    purpose: Literal["signup", "password_reset"] = "signup"


class OTPResponse(BaseModel):
    success: bool
    message: str
    expires_in_minutes: int = 10


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit numeric OTP")
    new_password: str = Field(..., min_length=6, description="New password minimum 6 chars")
