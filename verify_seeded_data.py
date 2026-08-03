import asyncio
import asyncpg
from core.config import settings

async def verify():
    conn = await asyncpg.connect(settings.DATABASE_URL)
    users = await conn.fetch("SELECT userid, name, email FROM users WHERE name IN ('saad', 'John Doe') OR email IN ('saadjamalsaifi@gmail.com', 'devayush402@gmail.com')")
    
    print("\n================ VERIFICATION RESULTS ================")
    for u in users:
        uid = u["userid"]
        name = u["name"]
        email = u["email"]
        
        stores_cnt = await conn.fetchval("SELECT COUNT(*) FROM stores WHERE userid = $1", uid)
        products_cnt = await conn.fetchval("SELECT COUNT(*) FROM products WHERE userid = $1", uid)
        orders_cnt = await conn.fetchval("SELECT COUNT(*) FROM orders WHERE userid = $1", uid)
        alerts_cnt = await conn.fetchval("SELECT COUNT(*) FROM inventory_alerts WHERE userid = $1", uid)
        dash = await conn.fetchrow("SELECT revenue, orders, units_sold, refunds, profit, average_order_value FROM dashboard_summary WHERE userid = $1", uid)
        
        print(f"\nUser: {name} ({email}) [ID: {uid}]")
        print(f"  Stores count: {stores_cnt}")
        print(f"  Products count: {products_cnt}")
        print(f"  Orders count: {orders_cnt}")
        print(f"  Inventory alerts count: {alerts_cnt}")
        if dash:
            print(f"  Dashboard summary: Revenue=${dash['revenue']:,.2f}, Orders={dash['orders']}, Units={dash['units_sold']}, Refunds=${dash['refunds']:,.2f}, Profit=${dash['profit']:,.2f}, AOV=${dash['average_order_value']:,.2f}")
        else:
            print("  Dashboard summary: None")
    
    print("======================================================")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(verify())
