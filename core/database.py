import asyncio
import logging
from typing import Optional
import asyncpg

from core.config import settings

logger = logging.getLogger(__name__)


class Database:

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._keep_alive_task: Optional[asyncio.Task] = None

    async def connect(self):
        if self.pool is not None:
            return
        try:
            self.pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=0,
                max_size=10,
                timeout=30.0,
                command_timeout=60.0,
                max_inactive_connection_lifetime=300.0,
            )
            logger.info("✅ PostgreSQL connected.")
            print("✅ PostgreSQL Connected")

            if self._keep_alive_task is None or self._keep_alive_task.done():
                self._keep_alive_task = asyncio.create_task(self._keep_alive_loop())
        except Exception as e:
            self.pool = None
            err_msg = str(e) or type(e).__name__
            logger.error(f"❌ PostgreSQL connection failed ({err_msg})")
            print(f"❌ PostgreSQL connection failed ({err_msg})")
            raise

    async def _keep_alive_loop(self):
        """Pings PostgreSQL every 60s to keep cloud DB connection alive."""
        while self.pool:
            try:
                await asyncio.sleep(60)
                if self.pool:
                    async with self.pool.acquire(timeout=5.0) as conn:
                        await conn.fetchval("SELECT 1;")
            except Exception:
                pass

    async def disconnect(self):
        if self._keep_alive_task:
            self._keep_alive_task.cancel()
            self._keep_alive_task = None
        if self.pool:
            try:
                await self.pool.close()
            except Exception:
                pass
            self.pool = None
            logger.info("❌ PostgreSQL connection closed.")

    async def acquire(self):
        return await self._acquire_with_retry()

    async def release(self, conn):
        if conn and self.pool:
            try:
                await self.pool.release(conn)
            except Exception:
                pass

    async def _acquire_with_retry(self, retries=4):
        last_err = None
        for attempt in range(retries):
            try:
                if self.pool is None:
                    await self.connect()
                return await self.pool.acquire(timeout=5.0)
            except Exception as e:
                last_err = e
                err_name = str(e) or type(e).__name__
                logger.warning(f"⚠️ DB connection acquire attempt {attempt + 1} failed ({err_name}). Retrying...")
                if attempt < retries - 1:
                    await asyncio.sleep(0.5)
        if last_err:
            raise last_err
        raise RuntimeError("Could not acquire database connection from pool.")

    async def fetchrow(self, query: str, *args, conn: Optional[asyncpg.Connection] = None):
        if conn:
            return await conn.fetchrow(query, *args)
        c = await self._acquire_with_retry()
        try:
            return await c.fetchrow(query, *args)
        finally:
            await self.release(c)

    async def fetch(self, query: str, *args, conn: Optional[asyncpg.Connection] = None):
        if conn:
            return await conn.fetch(query, *args)
        c = await self._acquire_with_retry()
        try:
            return await c.fetch(query, *args)
        finally:
            await self.release(c)

    async def fetchval(self, query: str, *args, conn: Optional[asyncpg.Connection] = None):
        if conn:
            return await conn.fetchval(query, *args)
        c = await self._acquire_with_retry()
        try:
            return await c.fetchval(query, *args)
        finally:
            await self.release(c)

    async def execute(self, query: str, *args, conn: Optional[asyncpg.Connection] = None):
        if conn:
            return await conn.execute(query, *args)
        c = await self._acquire_with_retry()
        try:
            return await c.execute(query, *args)
        finally:
            await self.release(c)

    async def executemany(self, query: str, args, conn: Optional[asyncpg.Connection] = None):
        if conn:
            return await conn.executemany(query, args)
        c = await self._acquire_with_retry()
        try:
            return await c.executemany(query, args)
        finally:
            await self.release(c)

    # Compatibility methods used by repositories
    async def fetch_one(self, query: str, *args, conn: Optional[asyncpg.Connection] = None):
        return await self.fetchrow(query, *args, conn=conn)

    async def fetch_all(self, query: str, *args, conn: Optional[asyncpg.Connection] = None):
        return await self.fetch(query, *args, conn=conn)


db = Database()