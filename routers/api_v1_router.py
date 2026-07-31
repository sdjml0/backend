from uuid import UUID
from fastapi import APIRouter, Depends

from core.dependencies import get_current_user
from schemas.dashboard import DashboardOverviewResponse
from services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/v1",
    tags=["V1 Analytics API"]
)


@router.get(
    "/dashboard/overview",
    response_model=DashboardOverviewResponse
)
async def get_dashboard_overview(
    userid: UUID = Depends(get_current_user)
):
    """
    Aggregated API payload for the entire analytics dashboard
    """
    return await DashboardService.get_overview(userid)


@router.get("/stores")
async def get_stores(
    userid: UUID = Depends(get_current_user)
):
    """
    List of connected marketplace stores
    """
    return await DashboardService.get_stores(userid)


@router.get("/metrics/kpi")
async def get_kpi_metrics(
    userid: UUID = Depends(get_current_user)
):
    """
    List of core KPI summary cards
    """
    return await DashboardService.get_kpi_metrics(userid)


@router.get("/analytics/revenue")
async def get_revenue_analytics(
    userid: UUID = Depends(get_current_user)
):
    """
    Revenue analytics time-series data over time
    """
    return await DashboardService.get_revenue_analytics(userid)


@router.get("/analytics/marketplace-share")
async def get_marketplace_share(
    userid: UUID = Depends(get_current_user)
):
    """
    Marketplace sales percentage breakdown
    """
    return await DashboardService.get_marketplace_shares(userid)


@router.get("/orders")
async def get_user_orders(
    userid: UUID = Depends(get_current_user)
):
    """
    List of orders associated with the user
    """
    return await DashboardService.get_user_orders(userid)


@router.get("/orders/recent")
async def get_recent_orders(
    userid: UUID = Depends(get_current_user)
):
    """
    List of recent orders
    """
    return await DashboardService.get_recent_orders(userid)


@router.get("/products")
async def get_user_products(
    userid: UUID = Depends(get_current_user)
):
    """
    List of products associated with the user
    """
    return await DashboardService.get_user_products(userid)


@router.get("/products/top-selling")
async def get_top_selling_products(
    userid: UUID = Depends(get_current_user)
):
    """
    Top selling product rankings
    """
    return await DashboardService.get_top_products(userid)


@router.get("/inventory")
async def get_inventory(
    userid: UUID = Depends(get_current_user)
):
    """
    List of all inventory stock items
    """
    return await DashboardService.get_user_inventory(userid)


@router.get("/inventory/alerts")
async def get_inventory_alerts(
    userid: UUID = Depends(get_current_user)
):
    """
    Inventory low stock alerts
    """
    return await DashboardService.get_inventory_alerts(userid)


