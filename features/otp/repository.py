import json
from typing import Any, Dict, Optional
from uuid import UUID

from core.database import db


class OTPRepository:

    @staticmethod
    async def save_otp(
        email: str,
        otp_code: str,
        purpose: str,
        expires_in_minutes: int = 10,
        payload: Optional[Dict[str, Any]] = None
    ) -> UUID:
        delete_query = """
            DELETE FROM otps
            WHERE LOWER(email) = LOWER($1) AND purpose = $2;
        """
        await db.execute(delete_query, email, purpose)

        payload_json = json.dumps(payload) if payload else None

        insert_query = """
            INSERT INTO otps (email, otp_code, purpose, payload, expires_at)
            VALUES (LOWER($1), $2, $3, $4::jsonb, CURRENT_TIMESTAMP + ($5 || ' minutes')::interval)
            RETURNING otpid;
        """
        return await db.fetchval(insert_query, email, otp_code, purpose, payload_json, str(expires_in_minutes))

    @staticmethod
    async def get_valid_otp(email: str, otp_code: str, purpose: str):
        query = """
            SELECT otpid, email, otp_code, purpose, payload, is_verified, created_at, expires_at
            FROM otps
            WHERE LOWER(email) = LOWER($1)
              AND otp_code = $2
              AND purpose = $3
              AND expires_at > CURRENT_TIMESTAMP;
        """
        return await db.fetchrow(query, email, otp_code, purpose)

    @staticmethod
    async def get_valid_otp_by_token(token: str):
        query = """
            SELECT otpid, email, otp_code, purpose, payload, is_verified, created_at, expires_at
            FROM otps
            WHERE otp_code = $1
              AND expires_at > CURRENT_TIMESTAMP;
        """
        return await db.fetchrow(query, token)

    @staticmethod
    async def mark_verified(otpid: UUID):
        query = """
            UPDATE otps
            SET is_verified = TRUE
            WHERE otpid = $1;
        """
        await db.execute(query, otpid)

    @staticmethod
    async def delete_otp(otpid: UUID):
        query = """
            DELETE FROM otps
            WHERE otpid = $1;
        """
        await db.execute(query, otpid)

    @staticmethod
    async def update_user_password(email: str, hashed_password: str):
        query = """
            UPDATE users
            SET password = $2
            WHERE LOWER(email) = LOWER($1);
        """
        return await db.execute(query, email, hashed_password)
