from uuid import UUID
from fastapi import APIRouter, Depends, status

from core.dependencies import get_current_user
from features.auth.schema import (
    LoginResponse,
    SignupResponse,
    UserLogin,
    UserSignup,
    UserUpdate,
    UserResponse
)
from features.auth.service import UserService
from features.otp.schema import (
    SendOTPRequest,
    VerifyOTPRequest,
    OTPResponse,
    ResetPasswordRequest,
)
from features.otp.service import OTPService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    summary="Register a new user account & send OTP verification code"
)
async def signup(user: UserSignup):
    """
    Registers user details and sends a 6-digit OTP code to the provided email.
    Account creation is completed upon verifying the OTP via `/auth/verify-otp`.
    """
    return await UserService.signup(user)


@router.post(
    "/send-otp",
    response_model=OTPResponse,
    summary="Request a 6-digit OTP email verification code"
)
async def send_otp(req: SendOTPRequest):
    """
    Dispatches a 6-digit numeric OTP code for email verification (`signup` or `password_reset`).
    """
    return await OTPService.send_otp(email=req.email, purpose=req.purpose)


@router.post(
    "/verify-otp",
    summary="Verify 6-digit OTP & finalize registration"
)
async def verify_otp(req: VerifyOTPRequest):
    """
    Validates a 6-digit OTP code. For `signup`, creates the user account and returns a JWT access token.
    """
    return await OTPService.verify_otp(email=req.email, otp_code=req.otp, purpose=req.purpose)


@router.post(
    "/reset-password",
    summary="Reset password using verified 6-digit OTP code"
)
async def reset_password(req: ResetPasswordRequest):
    """
    Resets the password for an existing user account after verifying the OTP code.
    """
    return await UserService.reset_password(req)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate user and receive JWT access token"
)
async def login(user_login: UserLogin):
    """
    Authenticates a user with email and password, returning a JWT token valid for 60 minutes.
    """
    return await UserService.login(user_login)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user profile"
)
async def get_current_user_profile(
    userid: UUID = Depends(get_current_user)
):
    """
    Retrieves profile information for the authenticated user based on the JWT Bearer token.
    """
    return await UserService.get_profile(userid)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update authenticated user profile"
)
async def update_current_user_profile(
    user_data: UserUpdate,
    userid: UUID = Depends(get_current_user)
):
    """
    Updates profile attributes (name, phone, address, city, postal code, country) for the authenticated user.
    """
    return await UserService.update_profile(userid, user_data)


@router.delete(
    "/me",
    summary="Delete authenticated user account"
)
async def delete_current_user_account(
    userid: UUID = Depends(get_current_user)
):
    """
    Deletes the authenticated user account and all associated data.
    """
    return await UserService.delete_account(userid)
