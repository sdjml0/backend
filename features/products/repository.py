from typing import List, Optional
from uuid import UUID

from core.database import db
from features.products.schema import ProductCreate, ProductUpdate


class ProductRepository:

    @staticmethod
    async def create_product(userid: UUID, product: ProductCreate):
        query = """
            INSERT INTO products (userid, product_name, units_sold, revenue)
            VALUES ($1, $2, $3, $4)
            RETURNING productid, userid, product_name, units_sold, revenue;
        """
        row = await db.fetchrow(
            query,
            userid,
            product.product_name,
            product.units_sold or 0,
            product.revenue or 0.0,
        )
        return dict(row) if row else None

    @staticmethod
    async def get_product_by_id(productid: UUID, userid: Optional[UUID] = None):
        if userid:
            query = """
                SELECT productid, userid, product_name, units_sold, revenue
                FROM products
                WHERE productid = $1 AND userid = $2;
            """
            row = await db.fetchrow(query, productid, userid)
        else:
            query = """
                SELECT productid, userid, product_name, units_sold, revenue
                FROM products
                WHERE productid = $1;
            """
            row = await db.fetchrow(query, productid)
        return dict(row) if row else None

    @staticmethod
    async def get_products_by_user(userid: UUID, limit: int = 50, offset: int = 0) -> List[dict]:
        query = """
            SELECT productid, userid, product_name, units_sold, revenue
            FROM products
            WHERE userid = $1
            ORDER BY productid
            LIMIT $2 OFFSET $3;
        """
        rows = await db.fetch(query, userid, limit, offset)
        return [dict(r) for r in rows]

    @staticmethod
    async def update_product(productid: UUID, userid: UUID, product_update: ProductUpdate):
        query = """
            UPDATE products
            SET 
                product_name = COALESCE($3, product_name),
                units_sold = COALESCE($4, units_sold),
                revenue = COALESCE($5, revenue)
            WHERE productid = $1 AND userid = $2
            RETURNING productid, userid, product_name, units_sold, revenue;
        """
        row = await db.fetchrow(
            query,
            productid,
            userid,
            product_update.product_name,
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
