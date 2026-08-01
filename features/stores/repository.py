from typing import List, Optional
from uuid import UUID

from core.database import db
from features.stores.schema import StoreCreate, StoreUpdate


class StoreRepository:

    @staticmethod
    async def create_store(userid: UUID, store: StoreCreate):
        query = """
            INSERT INTO stores (userid, platform, country, status)
            VALUES ($1, $2, $3, $4)
            RETURNING storeid, userid, platform, country, status;
        """
        row = await db.fetchrow(
            query,
            userid,
            store.platform,
            store.country or "Global",
            store.status or "connected",
        )
        return dict(row) if row else None

    @staticmethod
    async def get_store_by_id(storeid: UUID, userid: Optional[UUID] = None):
        if userid:
            query = """
                SELECT storeid, userid, platform, country, status
                FROM stores
                WHERE storeid = $1 AND userid = $2;
            """
            row = await db.fetchrow(query, storeid, userid)
        else:
            query = """
                SELECT storeid, userid, platform, country, status
                FROM stores
                WHERE storeid = $1;
            """
            row = await db.fetchrow(query, storeid)
        return dict(row) if row else None

    @staticmethod
    async def get_stores_by_user(userid: UUID, limit: int = 50, offset: int = 0) -> List[dict]:
        query = """
            SELECT storeid, userid, platform, country, status
            FROM stores
            WHERE userid = $1
            ORDER BY storeid
            LIMIT $2 OFFSET $3;
        """
        rows = await db.fetch(query, userid, limit, offset)
        return [dict(r) for r in rows]

    @staticmethod
    async def update_store(storeid: UUID, userid: UUID, store_update: StoreUpdate):
        query = """
            UPDATE stores
            SET 
                platform = COALESCE($3, platform),
                country = COALESCE($4, country),
                status = COALESCE($5, status)
            WHERE storeid = $1 AND userid = $2
            RETURNING storeid, userid, platform, country, status;
        """
        row = await db.fetchrow(
            query,
            storeid,
            userid,
            store_update.platform,
            store_update.country,
            store_update.status,
        )
        return dict(row) if row else None

    @staticmethod
    async def delete_store(storeid: UUID, userid: UUID) -> bool:
        query = """
            DELETE FROM stores
            WHERE storeid = $1 AND userid = $2
            RETURNING storeid;
        """
        deleted_id = await db.fetchval(query, storeid, userid)
        return deleted_id is not None
