from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP received via email")
    phone: Optional[str] = "1234567890"
    address: Optional[str] = "Main St"
    city: Optional[str] = "New York"
    postalcode: Optional[str] = "10001"
    country: Optional[str] = "United States"


class SignupResponse(BaseModel):
    message: str
    userid: UUID
    email: EmailStr
    accessToken: Optional[str] = None
    expiresIn: Optional[int] = 3600
    user: Optional[AuthUser] = None



class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    userid: UUID
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postalcode: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuthUser(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: Optional[str] = "Owner"


class LoginResponse(BaseModel):
    success: bool
    accessToken: str
    expiresIn: int
    user: AuthUser