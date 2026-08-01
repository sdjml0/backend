from typing import Optional
from uuid import UUID
import asyncpg
from core.database import db


class DashboardRepository:

    @staticmethod
    async def get_summary(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                revenue,
                orders,
                units_sold,
                refunds,
                profit,
                average_order_value
            FROM dashboard_summary
            WHERE userid=$1
        """
        return await db.fetch_one(query, userid, conn=conn)

    @staticmethod
    async def get_stores(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                s.storeid,
                s.platform,
                s.country,
                s.status,
                COALESCE(SUM(o.amount), 0) AS revenue
            FROM stores s
            LEFT JOIN orders o ON s.storeid = o.storeid AND o.userid = $1
            WHERE s.userid=$1
            GROUP BY s.storeid, s.platform, s.country, s.status
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_order_status(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                status,
                COUNT(*) AS count
            FROM orders
            WHERE userid=$1
            GROUP BY status
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_products(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                productid,
                product_name,
                units_sold,
                revenue
            FROM products
            WHERE userid=$1
            ORDER BY units_sold DESC
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_top_products(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                productid,
                product_name,
                units_sold,
                revenue
            FROM products
            WHERE userid=$1
            ORDER BY revenue DESC
            LIMIT 10
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_inventory(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                ia.alert_id,
                ia.productid,
                p.product_name,
                ia.stock,
                ia.alert_type
            FROM inventory_alerts ia
            JOIN products p ON ia.productid = p.productid
            WHERE ia.userid=$1
            ORDER BY ia.stock ASC
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_inventory_alerts(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                ia.productid,
                p.product_name,
                ia.stock,
                ia.alert_type
            FROM inventory_alerts ia
            JOIN products p ON ia.productid = p.productid
            WHERE ia.userid=$1
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_all_orders(userid: UUID, limit: int = 50, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                o.orderid,
                o.customer_name,
                o.customer_email,
                o.amount,
                o.status,
                o.created_at,
                s.platform AS marketplace
            FROM orders o
            LEFT JOIN stores s ON o.storeid = s.storeid
            WHERE o.userid=$1
            ORDER BY o.created_at DESC
            LIMIT $2
        """
        return await db.fetch_all(query, userid, limit, conn=conn)

    @staticmethod
    async def get_recent_orders(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                o.orderid,
                o.customer_name,
                o.customer_email,
                o.amount,
                o.status,
                o.created_at,
                s.platform AS marketplace
            FROM orders o
            LEFT JOIN stores s ON o.storeid = s.storeid
            WHERE o.userid=$1
            ORDER BY o.created_at DESC
            LIMIT 10
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_revenue_analytics(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                TO_CHAR(o.created_at, 'Mon DD') AS date_str,
                DATE(o.created_at) AS order_date,
                COALESCE(s.platform, 'Others') AS platform,
                SUM(o.amount) AS amount
            FROM orders o
            LEFT JOIN stores s ON o.storeid = s.storeid
            WHERE o.userid=$1
            GROUP BY order_date, date_str, platform
            ORDER BY order_date ASC
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_marketplace_shares(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                COALESCE(s.platform, 'Others') AS name,
                SUM(o.amount) AS revenue
            FROM orders o
            LEFT JOIN stores s ON o.storeid = s.storeid
            WHERE o.userid=$1
            GROUP BY name
            ORDER BY revenue DESC
        """
        return await db.fetch_all(query, userid, conn=conn)

    @staticmethod
    async def get_daily_trends(userid: UUID, conn: Optional[asyncpg.Connection] = None):
        query = """
            SELECT
                DATE(created_at) AS order_date,
                COUNT(*) AS orders_count,
                SUM(amount) AS total_revenue
            FROM orders
            WHERE userid=$1
            GROUP BY order_date
            ORDER BY order_date ASC
            LIMIT 7
        """
        return await db.fetch_all(query, userid, conn=conn)
