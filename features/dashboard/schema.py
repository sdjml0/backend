from pydantic import BaseModel
from typing import List, Optional, Literal


class StoreDTO(BaseModel):
    id: str
    name: str
    displayName: str
    country: str
    status: Literal["connected", "disconnected", "syncing"]
    revenue: str
    logoText: str
    brandColor: str


class SparklinePointDTO(BaseModel):
    val: float


class MetricDataDTO(BaseModel):
    id: str
    title: str
    value: str
    change: str
    isPositive: bool
    comparisonPeriod: str
    iconName: str
    color: str
    sparkline: List[SparklinePointDTO]


class RevenueDataPointDTO(BaseModel):
    date: str
    Amazon: float = 0.0
    Flipkart: float = 0.0
    eBay: float = 0.0
    Shopify: float = 0.0
    Others: float = 0.0
    total: float = 0.0

    model_config = {
        "extra": "allow"
    }


class MarketplaceShareDTO(BaseModel):
    name: str
    percentage: float
    revenue: str
    color: str


class OrderStatusShareDTO(BaseModel):
    name: Literal["Delivered", "Processing", "Shipped", "Cancelled"]
    count: int
    percentage: float
    color: str


class RecentOrderDTO(BaseModel):
    id: str
    orderNumber: str
    customerName: str
    customerEmail: str
    customerAvatar: Optional[str] = None
    marketplace: str
    date: str
    amount: str
    status: Literal["Delivered", "Processing", "Shipped", "Cancelled"]


class TopProductDTO(BaseModel):
    id: str
    name: str
    image: str
    unitsSold: int
    revenue: str


class InventoryAlertDTO(BaseModel):
    id: str
    name: str
    sku: str
    image: str
    stockLeft: int
    status: Literal["Low Stock", "Out of Stock"]


class DashboardDataDTO(BaseModel):
    connectedStores: List[StoreDTO]
    kpiMetrics: List[MetricDataDTO]
    revenueAnalytics: List[RevenueDataPointDTO]
    marketplaceShares: List[MarketplaceShareDTO]
    orderStatusShares: List[OrderStatusShareDTO]
    recentOrders: List[RecentOrderDTO]
    topProducts: List[TopProductDTO]
    inventoryAlerts: List[InventoryAlertDTO]


class DashboardOverviewResponse(BaseModel):
    status: str = "success"
    data: DashboardDataDTO
