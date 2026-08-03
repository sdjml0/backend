import asyncio
import json
import logging
import secrets
from typing import Optional
from fastapi import HTTPException, status

from core.config import settings
from core.security import create_access_token
from features.auth.repository import UserRepository
from features.auth.schema import UserSignup
from features.auth.service import EmailService
from features.otp.repository import OTPRepository

logger = logging.getLogger(__name__)


class MagicLinkService:

    @staticmethod
    def _generate_alphanumeric_token() -> str:
        """Generates a cryptographically secure 43-character URL-safe token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    async def send_magic_link(email: str, purpose: Optional[str] = None):
        """
        Generates and emails a magic link token for signup or password_reset.
        Token expires in 10 minutes.
        """
        user_exists = await UserRepository.user_exists(email)

        if not purpose:
            purpose = "password_reset" if user_exists else "signup"

        if purpose == "signup":
            if user_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists."
                )
        elif purpose == "password_reset":
            if not user_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User with this email was not found."
                )

        token_code = MagicLinkService._generate_alphanumeric_token()

        await OTPRepository.save_otp(
            email=email,
            otp_code=token_code,
            purpose=purpose,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES
        )

        await asyncio.to_thread(
            EmailService.send_magic_link_email,
            recipient_email=email,
            token_code=token_code,
            purpose=purpose
        )

        return {
            "success": True,
            "message": f"Magic link sent to {email}. It will expire in {settings.OTP_EXPIRE_MINUTES} minutes.",
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
        }

    # Backward compatibility alias
    send_otp = send_magic_link

    @staticmethod
    async def verify_link(token: str, email: Optional[str] = None):
        """
        Verifies magic link token from URL query params (`?token=...&email=...`).
        If signup token: Finalizes registration, creates user, generates fresh JWT token for auto-login.
        If password reset token: Validates active status and returns verification metadata.
        """
        otp_row = await OTPRepository.get_valid_otp_by_token(token)

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired magic link. Please request a new link."
            )

        if email and otp_row.get("email"):
            if otp_row["email"].lower() != email.strip().lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Magic link token does not match the provided email address."
                )

        otpid = otp_row["otpid"]
        record_email = otp_row["email"]
        purpose = otp_row["purpose"]
        payload_data = otp_row["payload"] if "payload" in otp_row and otp_row["payload"] else None

        if isinstance(payload_data, str):
            try:
                payload_data = json.loads(payload_data)
            except Exception:
                pass

        if purpose == "signup" and payload_data and isinstance(payload_data, dict):
            user_email = payload_data.get("email", record_email)
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
            "message": "Magic link token validated successfully.",
            "purpose": purpose,
            "email": record_email
        }

    # Backward compatibility alias
    verify_otp = verify_link


# Backward compatibility class alias
OTPService = MagicLinkService
