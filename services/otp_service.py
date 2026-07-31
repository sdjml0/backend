import asyncio
import logging
import secrets
from fastapi import HTTPException, status

from core.config import settings
from repositories.otp_repository import OTPRepository
from repositories.user_repository import UserRepository
from services.email_service import EmailService

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
        # Validate purpose rules
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

        # Generate 6-digit OTP
        otp_code = OTPService._generate_6_digit_otp()

        # Save OTP in database with 10-minute expiration
        await OTPRepository.save_otp(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES
        )

        # Dispatch OTP via email service in non-blocking worker thread
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
        """
        otp_row = await OTPRepository.get_valid_otp(email, otp_code, purpose)

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired 6-digit OTP code. Please request a new OTP."
            )

        # Mark OTP verified in DB
        await OTPRepository.mark_verified(otp_row["otpid"])

        return {
            "success": True,
            "message": "OTP validated successfully.",
            "otpid": otp_row["otpid"]
        }
