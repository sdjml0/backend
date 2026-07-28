import asyncio
import asyncpg
from core.config import settings

async def main():
    conn = await asyncpg.connect(settings.DATABASE_URL)
    stores = await conn.fetch("SELECT * FROM stores WHERE userid = $1", "5d09522b-a187-46bc-bf57-2c9b4407dddf")
    products = await conn.fetch("SELECT * FROM products WHERE userid = $1", "5d09522b-a187-46bc-bf57-2c9b4407dddf")
    orders = await conn.fetch("SELECT * FROM orders WHERE userid = $1", "5d09522b-a187-46bc-bf57-2c9b4407dddf")
    alerts = await conn.fetch("SELECT * FROM inventory_alerts WHERE userid = $1", "5d09522b-a187-46bc-bf57-2c9b4407dddf")
    
    print("✅ Live PostgreSQL Database Query Results:")
    print(f"Stores count in DB: {len(stores)}")
    print(f"Products count in DB: {len(products)}")
    print(f"Orders count in DB: {len(orders)}")
    print(f"Alerts count in DB: {len(alerts)}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
