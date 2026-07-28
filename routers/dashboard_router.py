from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from core.dependencies import get_current_user
from services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("")
async def get_dashboard(
    userid: Optional[UUID] = Depends(get_current_user)
):
    return await DashboardService.get_overview(userid)