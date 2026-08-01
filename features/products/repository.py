from typing import List, Optional
from uuid import UUID

from core.database import db
from features.products.schema import ProductCreate, ProductUpdate


class ProductRepository:

    @staticmethod
    async def create_product(userid: UUID, product: ProductCreate):
        query = """
            INSERT INTO products (userid, storeid, product_name, units_sold, revenue)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING productid, userid, storeid, product_name, units_sold, revenue;
        """
        row = await db.fetchrow(
            query,
            userid,
            product.storeid,
            product.product_name,
            product.units_sold or 0,
            product.revenue or 0.0,
        )
        return dict(row) if row else None

    @staticmethod
    async def get_product_by_id(productid: UUID, userid: Optional[UUID] = None):
        if userid:
            query = """
                SELECT productid, userid, storeid, product_name, units_sold, revenue
                FROM products
                WHERE productid = $1 AND userid = $2;
            """
            row = await db.fetchrow(query, productid, userid)
        else:
            query = """
                SELECT productid, userid, storeid, product_name, units_sold, revenue
                FROM products
                WHERE productid = $1;
            """
            row = await db.fetchrow(query, productid)
        return dict(row) if row else None

    @staticmethod
    async def get_products_count_by_user(userid: UUID, storeid: Optional[UUID] = None) -> int:
        query = """
            SELECT COUNT(*)
            FROM products
            WHERE userid = $1 AND ($2::uuid IS NULL OR storeid = $2::uuid);
        """
        val = await db.fetchval(query, userid, storeid)
        return val or 0

    @staticmethod
    async def get_products_by_user(
        userid: UUID, storeid: Optional[UUID] = None, limit: int = 10, offset: int = 0
    ) -> List[dict]:
        query = """
            SELECT productid, userid, storeid, product_name, units_sold, revenue
            FROM products
            WHERE userid = $1 AND ($2::uuid IS NULL OR storeid = $2::uuid)
            ORDER BY productid
            LIMIT $3 OFFSET $4;
        """
        rows = await db.fetch(query, userid, storeid, limit, offset)
        return [dict(r) for r in rows]

    @staticmethod
    async def get_products_paginated_by_user(
        userid: UUID, storeid: Optional[UUID] = None, limit: int = 10, offset: int = 0
    ) -> tuple[List[dict], int]:
        """
        Optimized single-query pagination using PostgreSQL Window Function COUNT(*) OVER().
        Supports filtering by optional storeid.
        Returns (items, total_count) in 1 database roundtrip.
        """
        query = """
            SELECT productid, userid, storeid, product_name, units_sold, revenue, COUNT(*) OVER() AS total_count
            FROM products
            WHERE userid = $1 AND ($2::uuid IS NULL OR storeid = $2::uuid)
            ORDER BY productid
            LIMIT $3 OFFSET $4;
        """
        rows = await db.fetch(query, userid, storeid, limit, offset)
        if not rows:
            if offset > 0:
                total = await ProductRepository.get_products_count_by_user(userid, storeid=storeid)
            else:
                total = 0
            return [], total

        total = rows[0]["total_count"]
        items = [
            {
                "productid": r["productid"],
                "userid": r["userid"],
                "storeid": r["storeid"],
                "product_name": r["product_name"],
                "units_sold": r["units_sold"],
                "revenue": r["revenue"],
            }
            for r in rows
        ]
        return items, total

    @staticmethod
    async def update_product(productid: UUID, userid: UUID, product_update: ProductUpdate):
        query = """
            UPDATE products
            SET 
                product_name = COALESCE($3, product_name),
                storeid = COALESCE($4, storeid),
                units_sold = COALESCE($5, units_sold),
                revenue = COALESCE($6, revenue)
            WHERE productid = $1 AND userid = $2
            RETURNING productid, userid, storeid, product_name, units_sold, revenue;
        """
        row = await db.fetchrow(
            query,
            productid,
            userid,
            product_update.product_name,
            product_update.storeid,
            product_update.units_sold,
            product_update.revenue,
        )
        return dict(row) if row else None


    @staticmethod
    async def delete_product(productid: UUID, userid: UUID) -> bool:
        query = """
            DELETE FROM products
            WHERE productid = $1 AND userid = $2
            RETURNING productid;
        """
        deleted_id = await db.fetchval(query, productid, userid)
        return deleted_id is not None
