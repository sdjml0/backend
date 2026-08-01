from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends

from core.dependencies import get_current_user
from features.dashboard.schema import DashboardOverviewResponse
from features.dashboard.service import DashboardService

router = APIRouter(
    prefix="",
    tags=["Dashboard & Analytics"]
)


@router.get(
    "/dashboard",
    summary="Get full dashboard summary"
)
@router.get(
    "/v1/dashboard/overview",
    response_model=DashboardOverviewResponse,
    summary="Aggregated API payload for analytics dashboard"
)
async def get_dashboard_overview(
    userid: UUID = Depends(get_current_user)
):
    return await DashboardService.get_overview(userid)


@router.get("/v1/stores", summary="List connected marketplace stores")
async def get_stores(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_stores(userid)


@router.get("/v1/metrics/kpi", summary="List core KPI summary cards")
async def get_kpi_metrics(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_kpi_metrics(userid)


@router.get("/v1/analytics/revenue", summary="Revenue time-series analytics")
async def get_revenue_analytics(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_revenue_analytics(userid)


@router.get("/v1/analytics/marketplace-share", summary="Marketplace sales share breakdown")
async def get_marketplace_share(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_marketplace_shares(userid)


@router.get("/v1/orders", summary="List user orders")
async def get_user_orders(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_user_orders(userid)


@router.get("/v1/orders/recent", summary="List recent orders")
async def get_recent_orders(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_recent_orders(userid)


@router.get("/v1/products/analytics", summary="List user products analytics")
async def get_user_products_analytics(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_user_products(userid)


@router.get("/v1/products/top-selling", summary="Top selling product rankings")
async def get_top_selling_products(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_top_products(userid)


@router.get("/v1/inventory", summary="List all inventory items")
async def get_inventory(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_user_inventory(userid)


@router.get("/v1/inventory/alerts", summary="Inventory low stock alerts")
async def get_inventory_alerts(userid: UUID = Depends(get_current_user)):
    return await DashboardService.get_inventory_alerts(userid)
