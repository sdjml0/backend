from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status

from schemas.user import (
    LoginResponse,
    SignupResponse,
    UserLogin,
    UserSignup,
    UserResponse
)

from services.user_service import UserService
from core.dependencies import get_current_user_optional

DEMO_USER_ID = UUID("5d09522b-a187-46bc-bf57-2c9b4407dddf")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    response_model=SignupResponse,
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
    userid: Optional[UUID] = Depends(get_current_user_optional)
):
    return await UserService.get_profile(userid)