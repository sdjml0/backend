import asyncio
import json
import logging
import secrets
from fastapi import HTTPException, status

from core.config import settings
from core.security import create_access_token
from features.auth.repository import UserRepository
from features.auth.schema import UserSignup
from features.auth.service import EmailService
from features.otp.repository import OTPRepository

logger = logging.getLogger(__name__)


class OTPService:

    @staticmethod
    def _generate_6_digit_otp() -> str:
        """Generates a cryptographically secure 6-digit numeric OTP code."""
        return "".join(secrets.choice("0123456789") for _ in range(6))

    @staticmethod
    async def send_otp(email: str, purpose: str = "signup"):
        """
        Generates and sends a 6-digit OTP to the user email for signup or password_reset.
        OTP expires in 10 minutes.
        """
        if purpose == "signup":
            exists = await UserRepository.user_exists(email)
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists."
                )
        elif purpose == "password_reset":
            exists = await UserRepository.user_exists(email)
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User with this email was not found."
                )

        otp_code = OTPService._generate_6_digit_otp()

        await OTPRepository.save_otp(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES
        )

        await asyncio.to_thread(
            EmailService.send_otp_email,
            recipient_email=email,
            otp_code=otp_code,
            purpose=purpose
        )

        return {
            "success": True,
            "message": f"6-digit OTP code sent to {email}. It will expire in {settings.OTP_EXPIRE_MINUTES} minutes.",
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
        }

    @staticmethod
    async def verify_otp(email: str, otp_code: str, purpose: str = "signup"):
        """
        Verifies that a 6-digit OTP code is valid and active (within 10 minutes).
        For 'signup' purpose with pending user payload, creates the user and returns JWT accessToken.
        """
        otp_row = await OTPRepository.get_valid_otp(email, otp_code, purpose)

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired 6-digit OTP code. Please request a new OTP."
            )

        otpid = otp_row["otpid"]
        payload_data = otp_row["payload"] if "payload" in otp_row and otp_row["payload"] else None

        if isinstance(payload_data, str):
            try:
                payload_data = json.loads(payload_data)
            except Exception:
                pass

        if purpose == "signup" and payload_data and isinstance(payload_data, dict):
            user_email = payload_data.get("email", email)
            exists = await UserRepository.user_exists(user_email)
            if exists:
                await OTPRepository.delete_otp(otpid)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists."
                )

            signup_user = UserSignup(
                name=payload_data.get("name", "User"),
                email=user_email,
                password="dummy_password",
                phone=payload_data.get("phone"),
                address=payload_data.get("address"),
                city=payload_data.get("city"),
                postalcode=payload_data.get("postalcode"),
                country=payload_data.get("country")
            )

            hashed_pwd = payload_data.get("password")
            userid = await UserRepository.create_user(user=signup_user, hashed_password=hashed_pwd)

            await OTPRepository.delete_otp(otpid)

            access_token = create_access_token(
                {
                    "sub": str(userid),
                    "name": signup_user.name,
                    "email": signup_user.email,
                    "phone": signup_user.phone,
                    "role": "Owner"
                }
            )

            return {
                "message": "User registered successfully.",
                "userid": str(userid),
                "email": signup_user.email,
                "accessToken": access_token,
                "expiresIn": 3600,
                "user": {
                    "id": str(userid),
                    "name": signup_user.name,
                    "email": signup_user.email,
                    "role": "Owner"
                }
            }

        await OTPRepository.mark_verified(otpid)

        return {
            "success": True,
            "message": "OTP validated successfully.",
            "otpid": otpid
        }
