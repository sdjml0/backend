from typing import Optional
from uuid import UUID

import asyncpg

from core.database import db
from schemas.user import UserSignup


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
    async def delete_user(userid: int):

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
    async def get_first_user():

        query = """
            SELECT *
            FROM users
            ORDER BY userid
            LIMIT 1
        """

        return await db.fetchrow(query)

