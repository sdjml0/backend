from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

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
    SendMagicLinkRequest,
    ForgotPasswordRequest,
    MagicLinkResponse,
    ResetPasswordRequest,
)
from features.otp.service import MagicLinkService

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
    "/forgot-password",
    response_model=MagicLinkResponse,
    summary="Request a password reset link for forgot password page"
)
async def forgot_password(req: ForgotPasswordRequest):
    """
    Dispatches a magic link email for resetting forgotten password.
    """
    return await MagicLinkService.send_magic_link(email=req.email, purpose="password_reset")


@router.post(
    "/forgotpassword",
    response_model=MagicLinkResponse,
    include_in_schema=False
)
async def forgot_password_alias(req: ForgotPasswordRequest):
    return await MagicLinkService.send_magic_link(email=req.email, purpose="password_reset")


@router.post(
    "/send-magic-link",
    response_model=MagicLinkResponse,
    summary="Request a magic link email for verification or password reset"
)
async def send_magic_link(req: SendMagicLinkRequest):
    """
    Dispatches a magic link email containing a 43-character URL-safe token (`signup` or `password_reset`).
    """
    return await MagicLinkService.send_magic_link(email=req.email, purpose=req.purpose)


# Alias for backward compatibility
@router.post(
    "/send-otp",
    response_model=MagicLinkResponse,
    summary="Alias for send-magic-link"
)
async def send_otp(req: SendMagicLinkRequest):
    return await MagicLinkService.send_magic_link(email=req.email, purpose=req.purpose)


@router.get(
    "/verify-link",
    summary="Verify magic link token from email URL"
)
async def verify_link(
    token: Optional[str] = Query(None),
    resetotp: Optional[str] = Query(None),
    otp: Optional[str] = Query(None),
    code: Optional[str] = Query(None)
):
    """
    Verifies the long alphanumeric magic link token from the email URL query param (`?token=...` or `?resetotp=...`).
    For `signup`, finalizes account creation and returns a fresh JWT access token for instant auto-login.
    For `password_reset`, validates token expiration before rendering the new password form.
    """
    active_token = token or resetotp or otp or code
    return await MagicLinkService.verify_link(active_token)


@router.post(
    "/reset-password",
    summary="Reset password using valid magic link token"
)
async def reset_password(req: ResetPasswordRequest):
    """
    Resets user password in PostgreSQL database using magic link token and returns a fresh JWT access token.
    """
    return await UserService.reset_password(req)


@router.post(
    "/resetpassword",
    include_in_schema=False
)
async def reset_password_alias(req: ResetPasswordRequest):
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
