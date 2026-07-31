from uuid import UUID
from fastapi import APIRouter, Depends, status

from schemas.otp import (
    SendOTPRequest,
    VerifyOTPRequest,
    OTPResponse,
    ResetPasswordRequest,
)
from schemas.user import (
    LoginResponse,
    SignupResponse,
    UserLogin,
    UserSignup,
    UserResponse
)
from services.otp_service import OTPService
from services.user_service import UserService
from core.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/send-otp",
    response_model=OTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a 6-digit OTP code to the client email for email verification or password reset"
)
async def send_otp(req: SendOTPRequest):
    """
    Sends a 6-digit random OTP to the provided email address for verification (valid for 10 minutes).
    - **purpose**: 'signup' or 'password_reset'
    """
    return await OTPService.send_otp(email=req.email, purpose=req.purpose)


@router.post(
    "/verify-otp",
    status_code=status.HTTP_200_OK,
    summary="Verify 6-digit OTP code before signup or password reset"
)
async def verify_otp(req: VerifyOTPRequest):
    """
    Validates that the provided 6-digit OTP code matches and is within the 10-minute validity window.
    """
    return await OTPService.verify_otp(email=req.email, otp_code=req.otp, purpose=req.purpose)


@router.post(
    "/signup",
    response_model=SignupResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup with mandatory OTP verification"
)
async def signup(user: UserSignup):
    """
    Validates the 6-digit OTP provided in user payload. If OTP is validated, user credentials are saved in the DB.
    """
    return await UserService.signup(user)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login"
)
async def login(user: UserLogin):
    return await UserService.login(user)


@router.get("/login")
async def login_info():
    return {
        "message": "Authentication endpoint active. Send a POST request with email and password.",
        "status": "ok"
    }


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset password using verified 6-digit OTP"
)
async def reset_password(req: ResetPasswordRequest):
    """
    Resets user password after verifying the 6-digit OTP code sent to their email.
    """
    return await UserService.reset_password(req)


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get logged-in user profile"
)
async def profile(
    userid: UUID = Depends(get_current_user)
):
    return await UserService.get_profile(userid)


@router.post(
    "/profile/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Profile Password Reset using 6-digit OTP"
)
async def profile_reset_password(
    req: ResetPasswordRequest,
    userid: UUID = Depends(get_current_user)
):
    """
    Allows logged in users to reset their profile password using an OTP sent to their email.
    """
    user_profile = await UserService.get_profile(userid)
    if user_profile.email.lower() != req.email.lower():
        req.email = user_profile.email

    return await UserService.reset_password(req)