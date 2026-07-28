from uuid import UUID

from fastapi import HTTPException, status

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from repositories.user_repository import UserRepository

from schemas.user import (
    UserLogin,
    UserResponse,
    UserSignup,
    LoginResponse
)


class UserService:

    @staticmethod
    async def signup(user: UserSignup):

        # Check if email already exists
        exists = await UserRepository.user_exists(user.email)

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists."
            )

        # Hash password
        hashed_password = hash_password(user.password)

        # Save user
        userid = await UserRepository.create_user(
            user=user,
            hashed_password=hashed_password
        )

        return {
            "message": "User registered successfully.",
            "userid": str(userid)
        }


    @staticmethod
    async def login(login: UserLogin) -> LoginResponse:

        user = await UserRepository.get_user_by_email(
            login.email
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )


        if not verify_password(
            login.password,
            user["password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password."
            )


        access_token = create_access_token(
            {
                "sub": str(user["userid"]),
                "name": user["name"]
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
                "role": dict(user).get("role", "Owner")
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


        return UserResponse(
            userid=user["userid"],
            name=user["name"],
            email=user["email"],
            phone=user["phone"],
            address=user["address"],
            city=user["city"],
            postalcode=user["postalcode"],
            country=user["country"],
        )