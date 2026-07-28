import asyncio
import asyncpg
from core.config import settings

async def seed_database():
    print(f"Connecting to Database: {settings.DATABASE_URL.split('@')[-1]}...")
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    with open("seed.sql", "r") as f:
        sql_script = f.read()

    print("Executing seed.sql script on PostgreSQL database...")
    await conn.execute(sql_script)
    print("✅ Seed script executed successfully! 10 rows inserted per table for user 5d09522b-a187-46bc-bf57-2c9b4407dddf.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
