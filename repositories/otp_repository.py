from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from core.database import db


class OTPRepository:

    @staticmethod
    async def save_otp(email: str, otp_code: str, purpose: str, expires_in_minutes: int = 10) -> UUID:
        """Invalidates existing active OTPs for email+purpose and creates a new one with expiration."""
        # Clean up existing unverified OTPs for this email and purpose
        delete_query = """
            DELETE FROM otps
            WHERE LOWER(email) = LOWER($1) AND purpose = $2;
        """
        await db.execute(delete_query, email, purpose)

        # Insert new OTP with expiration interval
        insert_query = """
            INSERT INTO otps (email, otp_code, purpose, expires_at)
            VALUES (LOWER($1), $2, $3, CURRENT_TIMESTAMP + ($4 || ' minutes')::interval)
            RETURNING otpid;
        """
        return await db.fetchval(insert_query, email, otp_code, purpose, str(expires_in_minutes))

    @staticmethod
    async def get_valid_otp(email: str, otp_code: str, purpose: str):
        """Fetches active non-expired OTP row."""
        query = """
            SELECT otpid, email, otp_code, purpose, is_verified, created_at, expires_at
            FROM otps
            WHERE LOWER(email) = LOWER($1)
              AND otp_code = $2
              AND purpose = $3
              AND expires_at > CURRENT_TIMESTAMP;
        """
        return await db.fetchrow(query, email, otp_code, purpose)

    @staticmethod
    async def mark_verified(otpid: UUID):
        """Marks an OTP as verified."""
        query = """
            UPDATE otps
            SET is_verified = TRUE
            WHERE otpid = $1;
        """
        await db.execute(query, otpid)

    @staticmethod
    async def delete_otp(otpid: UUID):
        """Deletes OTP after consumption."""
        query = """
            DELETE FROM otps
            WHERE otpid = $1;
        """
        await db.execute(query, otpid)

    @staticmethod
    async def update_user_password(email: str, hashed_password: str):
        """Updates user's password in users table by email."""
        query = """
            UPDATE users
            SET password = $2
            WHERE LOWER(email) = LOWER($1);
        """
        return await db.execute(query, email, hashed_password)
