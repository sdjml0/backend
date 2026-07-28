from uuid import UUID

from fastapi import APIRouter, Depends, status

from schemas.user import (
    LoginResponse,
    UserLogin,
    UserSignup,
    UserResponse
)

from services.user_service import UserService
from core.dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
)
async def signup(user: UserSignup):

    return await UserService.signup(user)



@router.post(
    "/login",
    response_model=LoginResponse
)
async def login(user: UserLogin):

    return await UserService.login(user)



@router.get(
    "/profile",
    response_model=UserResponse
)
async def profile(
    userid: UUID = Depends(get_current_user)
):

    return await UserService.get_profile(userid)