import asyncio
from typing import Optional, List, Dict, Any
from uuid import UUID
from core.database import db
from repositories.dashboard_repository import DashboardRepository

DEMO_USER_ID = UUID("5d09522b-a187-46bc-bf57-2c9b4407dddf")

PLATFORM_COLORS = {
    "Amazon": "#0F4C81",
    "Flipkart": "#14B8A6",
    "eBay": "#F59E0B",
    "Shopify": "#22C55E",
    "WooCommerce": "#64748B",
    "Etsy": "#F97316",
    "Walmart": "#0284C7",
    "Rakuten": "#818CF8",
    "Mercado Libre": "#FACC15",
    "Alibaba": "#E11D48",
    "Others": "#94A3B8"
}

STATUS_COLORS = {
    "Delivered": "#22C55E",
    "Processing": "#0F4C81",
    "Shipped": "#F59E0B",
    "Cancelled": "#EF4444",
}


import time

_OVERVIEW_CACHE: Dict[str, Any] = {}
_CACHE_TIMESTAMP: Dict[str, float] = {}
CACHE_TTL_SECONDS = 15.0


class DashboardService:

    @staticmethod
    async def get_overview(userid: Optional[UUID] = None) -> Dict[str, Any]:
        target_user = userid or DEMO_USER_ID
        cache_key = str(target_user)

        now = time.time()
        if cache_key in _OVERVIEW_CACHE and (now - _CACHE_TIMESTAMP.get(cache_key, 0)) < CACHE_TTL_SECONDS:
            return _OVERVIEW_CACHE[cache_key]

        conn = None
        try:
            conn = await db.acquire()
            results = await asyncio.gather(
                DashboardRepository.get_summary(target_user, conn=conn),
                DashboardRepository.get_stores(target_user, conn=conn),
                DashboardRepository.get_top_products(target_user, conn=conn),
                DashboardRepository.get_inventory_alerts(target_user, conn=conn),
                DashboardRepository.get_recent_orders(target_user, conn=conn),
                DashboardRepository.get_order_status(target_user, conn=conn),
                DashboardRepository.get_revenue_analytics(target_user, conn=conn),
                DashboardRepository.get_marketplace_shares(target_user, conn=conn),
                DashboardRepository.get_daily_trends(target_user, conn=conn),
                return_exceptions=True
            )

            db_summary = results[0] if not isinstance(results[0], Exception) else None
            db_stores = results[1] if not isinstance(results[1], Exception) else None
            db_products = results[2] if not isinstance(results[2], Exception) else None
            db_alerts = results[3] if not isinstance(results[3], Exception) else None
            db_orders = results[4] if not isinstance(results[4], Exception) else None
            db_order_status = results[5] if not isinstance(results[5], Exception) else None
            db_revenue_analytics = results[6] if not isinstance(results[6], Exception) else None
            db_marketplace_shares = results[7] if not isinstance(results[7], Exception) else None
            db_daily_trends = results[8] if not isinstance(results[8], Exception) else None

            # 1. Process Connected Stores
            stores = []
            if db_stores:
                for s in db_stores:
                    platform_name = s["platform"] or "Store"
                    rev_val = float(s["revenue"]) if s["revenue"] is not None else 0.0
                    stores.append({
                        "id": str(s["storeid"]),
                        "name": platform_name,
                        "displayName": platform_name,
                        "country": s["country"] or "Global",
                        "status": s["status"] if s["status"] in ["connected", "disconnected", "syncing"] else "connected",
                        "revenue": f"${rev_val:,.2f}",
                        "logoText": platform_name[0].lower() if platform_name else "s",
                        "brandColor": PLATFORM_COLORS.get(platform_name, "#0F4C81"),
                    })

            # 2. Process Top Products
            top_products = []
            if db_products:
                for p in db_products:
                    raw_pid = str(p["productid"])
                    top_products.append({
                        "id": raw_pid,
                        "name": p["product_name"],
                        "sku": f"SKU: PRD-{raw_pid[:8].upper()}",
                        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=150&auto=format&fit=crop&q=80",
                        "unitsSold": p["units_sold"] or 0,
                        "revenue": f"${float(p['revenue'] or 0.0):,.2f}",
                    })

            # 3. Process Inventory Alerts
            inventory_alerts = []
            if db_alerts:
                for a in db_alerts:
                    raw_pid = str(a["productid"])
                    inventory_alerts.append({
                        "id": raw_pid,
                        "name": a["product_name"],
                        "sku": f"SKU: PRD-{raw_pid[:8].upper()}",
                        "image": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=150&auto=format&fit=crop&q=80",
                        "stockLeft": a["stock"],
                        "status": a["alert_type"] if a["alert_type"] in ["Low Stock", "Out of Stock"] else "Low Stock",
                    })

            # 4. Process Recent Orders
            recent_orders = []
            if db_orders:
                for o in db_orders:
                    created_date = o["created_at"].strftime("%b %d, %Y") if o["created_at"] else "Jul 15, 2025"
                    raw_id = str(o["orderid"])
                    recent_orders.append({
                        "id": raw_id,
                        "orderNumber": f"#ORD-{raw_id[:8].upper()}",
                        "customerName": o["customer_name"] or "Customer",
                        "customerEmail": o["customer_email"] or "customer@example.com",
                        "marketplace": o["marketplace"] or "Amazon",
                        "date": created_date,
                        "amount": f"${float(o['amount'] or 0.0):,.2f}",
                        "status": o["status"] if o["status"] in ["Delivered", "Processing", "Shipped", "Cancelled"] else "Delivered",
                    })

            # 5. Process Order Status Shares
            order_status_shares = []
            if db_order_status:
                total_status_count = sum(r["count"] for r in db_order_status) or 1
                for r in db_order_status:
                    st_name = r["status"]
                    cnt = r["count"]
                    order_status_shares.append({
                        "name": st_name,
                        "count": cnt,
                        "percentage": round((cnt / total_status_count) * 100, 1),
                        "color": STATUS_COLORS.get(st_name, "#64748B"),
                    })

            # 6. Process Revenue Analytics Time Series
            revenue_analytics = []
            if db_revenue_analytics:
                date_groups: Dict[str, Dict[str, Any]] = {}
                for row in db_revenue_analytics:
                    d_str = row["date_str"]
                    platform = row["platform"]
                    amt = float(row["amount"] or 0.0)

                    if d_str not in date_groups:
                        date_groups[d_str] = {
                            "date": d_str,
                            "Amazon": 0.0,
                            "Flipkart": 0.0,
                            "eBay": 0.0,
                            "Shopify": 0.0,
                            "Others": 0.0,
                            "total": 0.0
                        }
                    
                    date_groups[d_str][platform] = amt
                    date_groups[d_str]["total"] += round(amt, 2)

                revenue_analytics = list(date_groups.values())

            # 7. Process Marketplace Shares
            marketplace_shares = []
            if db_marketplace_shares:
                total_mkt_revenue = sum(float(r["revenue"] or 0.0) for r in db_marketplace_shares) or 1.0
                for r in db_marketplace_shares:
                    name = r["name"]
                    rev = float(r["revenue"] or 0.0)
                    marketplace_shares.append({
                        "name": name,
                        "percentage": round((rev / total_mkt_revenue) * 100, 1),
                        "revenue": f"${rev:,.2f}",
                        "color": PLATFORM_COLORS.get(name, "#64748B"),
                    })

            # 8. Process Sparklines & KPI Metrics
            rev_sparkline = []
            orders_sparkline = []
            if db_daily_trends:
                for row in db_daily_trends:
                    rev_sparkline.append({"val": float(row["total_revenue"] or 0.0)})
                    orders_sparkline.append({"val": int(row["orders_count"] or 0)})

            if not rev_sparkline:
                rev_sparkline = [{"val": 0}]
            if not orders_sparkline:
                orders_sparkline = [{"val": 0}]

            d = dict(db_summary) if db_summary else {}
            kpi_metrics = [
                {
                    "id": "metric-revenue",
                    "title": "Total Revenue",
                    "value": f"${float(d.get('revenue', 0.0)):,.2f}",
                    "change": "18.5%",
                    "isPositive": True,
                    "comparisonPeriod": "vs last 7 days",
                    "iconName": "DollarSign",
                    "color": "#0F4C81",
                    "sparkline": rev_sparkline,
                },
                {
                    "id": "metric-orders",
                    "title": "Total Orders",
                    "value": f"{int(d.get('orders', 0)):,}",
                    "change": "15.3%",
                    "isPositive": True,
                    "comparisonPeriod": "vs last 7 days",
                    "iconName": "ShoppingCart",
                    "color": "#14B8A6",
                    "sparkline": orders_sparkline,
                },
                {
                    "id": "metric-units",
                    "title": "Total Units Sold",
                    "value": f"{int(d.get('units_sold', 0)):,}",
                    "change": "12.7%",
                    "isPositive": True,
                    "comparisonPeriod": "vs last 7 days",
                    "iconName": "Package",
                    "color": "#0F4C81",
                    "sparkline": orders_sparkline,
                },
                {
                    "id": "metric-refunds",
                    "title": "Total Refunds",
                    "value": f"${float(d.get('refunds', 0.0)):,.2f}",
                    "change": "6.3%",
                    "isPositive": False,
                    "comparisonPeriod": "vs last 7 days",
                    "iconName": "RotateCcw",
                    "color": "#EF4444",
                    "sparkline": rev_sparkline,
                },
                {
                    "id": "metric-profit",
                    "title": "Total Profit",
                    "value": f"${float(d.get('profit', 0.0)):,.2f}",
                    "change": "20.1%",
                    "isPositive": True,
                    "comparisonPeriod": "vs last 7 days",
                    "iconName": "TrendingUp",
                    "color": "#22C55E",
                    "sparkline": rev_sparkline,
                },
                {
                    "id": "metric-aov",
                    "title": "Avg. Order Value",
                    "value": f"${float(d.get('average_order_value', 0.0)):,.2f}",
                    "change": "2.8%",
                    "isPositive": True,
                    "comparisonPeriod": "vs last 7 days",
                    "iconName": "Tag",
                    "color": "#14B8A6",
                    "sparkline": rev_sparkline,
                },
            ]

        except Exception as e:
            err_name = str(e) or type(e).__name__
            print(f"Error querying database in DashboardService ({err_name})")
            stores = []
            top_products = []
            inventory_alerts = []
            recent_orders = []
            order_status_shares = []
            revenue_analytics = []
            marketplace_shares = []
            kpi_metrics = []

        finally:
            if conn:
                await db.release(conn)

        res_dict = {
            "status": "success",
            "data": {
                "connectedStores": stores,
                "kpiMetrics": kpi_metrics,
                "revenueAnalytics": revenue_analytics,
                "marketplaceShares": marketplace_shares,
                "orderStatusShares": order_status_shares,
                "recentOrders": recent_orders,
                "topProducts": top_products,
                "inventoryAlerts": inventory_alerts,
            }
        }
        if stores or kpi_metrics or recent_orders:
            _OVERVIEW_CACHE[cache_key] = res_dict
            _CACHE_TIMESTAMP[cache_key] = time.time()

        return res_dict

    @staticmethod
    async def get_stores(userid: Optional[UUID] = None) -> List[Dict[str, Any]]:
        overview = await DashboardService.get_overview(userid)
        return overview.get("data", {}).get("connectedStores", [])

    @staticmethod
    async def get_kpi_metrics(userid: Optional[UUID] = None) -> List[Dict[str, Any]]:
        overview = await DashboardService.get_overview(userid)
        return overview.get("data", {}).get("kpiMetrics", [])

    @staticmethod
    async def get_revenue_analytics(userid: Optional[UUID] = None) -> List[Dict[str, Any]]:
        overview = await DashboardService.get_overview(userid)
        return overview.get("data", {}).get("revenueAnalytics", [])

    @staticmethod
    async def get_marketplace_shares(userid: Optional[UUID] = None) -> List[Dict[str, Any]]:
        overview = await DashboardService.get_overview(userid)
        return overview.get("data", {}).get("marketplaceShares", [])

    @staticmethod
    async def get_recent_orders(userid: Optional[UUID] = None) -> List[Dict[str, Any]]:
        overview = await DashboardService.get_overview(userid)
        return overview.get("data", {}).get("recentOrders", [])

    @staticmethod
    async def get_top_products(userid: Optional[UUID] = None) -> List[Dict[str, Any]]:
        overview = await DashboardService.get_overview(userid)
        return overview.get("data", {}).get("topProducts", [])

    @staticmethod
    async def get_inventory_alerts(userid: Optional[UUID] = None) -> List[Dict[str, Any]]:
        overview = await DashboardService.get_overview(userid)
        return overview.get("data", {}).get("inventoryAlerts", [])