from typing import Optional
from uuid import UUID

from core.database import db
from features.auth.schema import UserSignup, UserUpdate


class UserRepository:

    @staticmethod
    async def create_user(user: UserSignup, hashed_password: str):
        query = """
            INSERT INTO users
            (
                name,
                email,
                phone,
                address,
                city,
                postalcode,
                country,
                password
            )
            VALUES
            (
                $1,$2,$3,$4,$5,$6,$7,$8
            )
            RETURNING userid;
        """
        return await db.fetchval(
            query,
            user.name,
            user.email,
            user.phone,
            user.address,
            user.city,
            user.postalcode,
            user.country,
            hashed_password
        )

    @staticmethod
    async def get_user_by_id(userid: UUID):
        query = """
            SELECT *
            FROM users
            WHERE userid=$1
        """
        return await db.fetchrow(query, userid)

    @staticmethod
    async def user_exists(email: str):
        query = """
            SELECT EXISTS(
                SELECT 1
                FROM users
                WHERE email=$1
            )
        """
        return await db.fetchval(query, email)

    @staticmethod
    async def delete_user(userid: UUID):
        query = """
            DELETE FROM users
            WHERE userid=$1
        """
        return await db.execute(query, userid)

    @staticmethod
    async def get_all_users():
        query = """
            SELECT
                userid,
                name,
                address,
                city,
                postalcode,
                country
            FROM users
            ORDER BY userid
        """
        return await db.fetch(query)

    @staticmethod
    async def get_user_by_email(email: str):
        query = """
            SELECT *
            FROM users
            WHERE email=$1
        """
        return await db.fetchrow(query, email)

    @staticmethod
    async def update_user(userid: UUID, user_update: UserUpdate):
        postalcode = user_update.get_postalcode() if hasattr(user_update, "get_postalcode") else user_update.postalcode
        query = """
            UPDATE users
            SET 
                name = COALESCE($2, name),
                phone = COALESCE($3, phone),
                address = COALESCE($4, address),
                city = COALESCE($5, city),
                postalcode = COALESCE($6, postalcode),
                country = COALESCE($7, country)
            WHERE userid = $1
            RETURNING *;
        """
        row = await db.fetchrow(
            query,
            userid,
            user_update.name,
            user_update.phone,
            user_update.address,
            user_update.city,
            postalcode,
            user_update.country
        )
        return dict(row) if row else None

    @staticmethod
    async def get_first_user():
        query = """
            SELECT *
            FROM users
            ORDER BY userid
            LIMIT 1
        """
        return await db.fetchrow(query)
