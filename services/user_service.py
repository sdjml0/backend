from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status

from core.config import settings
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from repositories.otp_repository import OTPRepository
from repositories.user_repository import UserRepository
from schemas.otp import ResetPasswordRequest
from schemas.user import (
    UserLogin,
    UserResponse,
    UserSignup,
    LoginResponse
)
from services.otp_service import OTPService


class UserService:

    @staticmethod
    async def signup(user: UserSignup):
        # 1. Check if user already exists
        exists = await UserRepository.user_exists(user.email)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists."
            )

        # 2. Hash password
        hashed_password = hash_password(user.password)

        # 3. Standard 2-Step Signup Workflow:
        # Generate 6-digit OTP code & save pending registration payload in otps DB table
        otp_code = OTPService._generate_6_digit_otp()
        payload = {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "phone": user.phone,
            "address": user.address,
            "city": user.city,
            "postalcode": user.postalcode,
            "country": user.country,
        }

        await OTPRepository.save_otp(
            email=user.email,
            otp_code=otp_code,
            purpose="signup",
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
            payload=payload
        )

        # Dispatch OTP via email service in non-blocking worker thread
        import asyncio
        from services.email_service import EmailService
        await asyncio.to_thread(
            EmailService.send_otp_email,
            recipient_email=user.email,
            otp_code=otp_code,
            purpose="signup"
        )

        return {
            "success": True,
            "message": f"Registration details received. 6-digit OTP code sent to {user.email}. Please verify OTP to complete account creation.",
            "email": user.email,
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
        }

    @staticmethod
    async def reset_password(req: ResetPasswordRequest):
        # 1. Verify OTP first (must be valid, active within 10 minutes for password_reset)
        otp_res = await OTPService.verify_otp(
            email=req.email,
            otp_code=req.otp,
            purpose="password_reset"
        )

        # 2. Check user exists
        user = await UserRepository.get_user_by_email(req.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        # 3. Hash new password & update DB
        hashed_password = hash_password(req.new_password)
        await OTPRepository.update_user_password(req.email, hashed_password)

        # 4. Clean up consumed OTP
        if "otpid" in otp_res:
            await OTPRepository.delete_otp(otp_res["otpid"])

        return {
            "success": True,
            "message": "Password reset successfully. You can now login with your new password."
        }

    @staticmethod
    async def login(login: UserLogin) -> LoginResponse:
        user = await UserRepository.get_user_by_email(login.email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        if not verify_password(login.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password."
            )

        user_dict = dict(user)

        access_token = create_access_token(
            {
                "sub": str(user["userid"]),
                "name": user["name"],
                "email": user["email"],
                "phone": user_dict.get("phone"),
                "role": user_dict.get("role", "Owner")
            }
        )

        return LoginResponse(
            success=True,
            accessToken=access_token,
            expiresIn=3600,
            user={
                "id": user["userid"],
                "name": user["name"],
                "email": user["email"],
                "role": user_dict.get("role", "Owner")
            }
        )

    @staticmethod
    async def get_profile(userid: UUID):
        user = await UserRepository.get_user_by_id(userid)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        user_dict = dict(user)

        return UserResponse(
            userid=user["userid"],
            name=user["name"],
            email=user["email"],
            phone=user_dict.get("phone"),
            address=user_dict.get("address"),
            city=user_dict.get("city"),
            postalcode=user_dict.get("postalcode"),
            country=user_dict.get("country"),
        )