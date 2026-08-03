import asyncio
import random
import uuid
from datetime import datetime, timedelta
import asyncpg
from core.config import settings

PRODUCT_NAMES = [
    "Wireless Noise Cancelling Headphones", "Smartwatch Series 8", "Ergonomic Mechanical Keyboard",
    "Ultra-HD 4K Gaming Monitor 27\"", "Portable Bluetooth Speaker", "USB-C Multiport Adapter",
    "Ergonomic Wireless Vertical Mouse", "Fast Charging Power Bank 20000mAh", "HD Webcam 1080p",
    "Laptop Stand Adjustable Aluminum", "Smart RGB LED Light Strip", "Compact Wireless Earbuds",
    "External SSD 1TB Portable", "Dual Monitor Mount Arm", "High-Speed HDMI 2.1 Cable",
    "Noise-Isolating Gaming Headset", "Smart Home Security Camera", "MagSafe Wireless Charger",
    "Bluetooth Fitness Tracker", "Mechanical Numpad", "Desk Pad Large Felt",
    "Stainless Steel Water Bottle 1L", "Organic Cotton Hoodie", "Slim Minimalist Wallet",
    "Polarized Sunglasses UV400", "Travel Backpack 35L", "Stainless Steel Coffee Tumbler",
    "Running Shoes Mesh Breathable", "Leather Journal Notebook", "Ceramic Mug Set of 4",
    "Resistance Bands Exercise Set", "Yoga Mat Non-Slip", "Adjustable Dumbbells Pair",
    "Air Purifier HEPA Filter", "Electric Toothbrush Sonic", "Aroma Essential Oil Diffuser",
    "Smart Scale Bluetooth Body Fat", "Deep Tissue Massage Gun", "Memory Foam Pillow",
    "Stainless Steel Cookware Set", "Non-Stick Frying Pan 10\"", "Chef Knife 8 Inch German Steel",
    "Automatic Coffee Maker Drip", "Electric Tea Kettle Stainless", "Digital Kitchen Scale",
    "Smart Door Lock Fingerprint", "Solar Power Outdoor Light", "Robot Vacuum Cleaner",
    "Portable Mini Projector", "Smart Plug Wi-Fi Outlet"
]

STORE_PLATFORMS = [
    ("Amazon", "United States"),
    ("Shopify", "Global"),
    ("Flipkart", "India"),
    ("eBay", "Global"),
    ("WooCommerce", "United States"),
    ("Walmart", "United States"),
    ("Etsy", "United States"),
]

CUSTOMER_NAMES = [
    "Alex Morgan", "Priya Sharma", "David Miller", "Sarah Jenkins", "Michael Chen",
    "Elena Rostova", "Kenji Sato", "Lucas Silva", "Chloe Dubois", "Liam O'Connor",
    "Emma Watson", "Noah Smith", "Olivia Johnson", "James Wilson", "Sophia Martinez",
    "Benjamin Taylor", "Ava Anderson", "Mason Thomas", "Isabella White", "Ethan Harris"
]

STATUSES = ["Delivered", "Delivered", "Delivered", "Processing", "Shipped", "Cancelled"]

async def seed():
    print("Connecting to database...")
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    # 1. Fetch Saad and John Doe user records
    saad_user = await conn.fetchrow("SELECT userid, name, email FROM users WHERE name = 'saad' OR email LIKE '%saad%'")
    john_user = await conn.fetchrow("SELECT userid, name, email FROM users WHERE name ILIKE '%john%' OR email LIKE '%devayush%' OR name ILIKE '%jane%'")
    
    if not saad_user:
        saad_id = uuid.uuid4()
        await conn.execute(
            "INSERT INTO users (userid, name, email, password) VALUES ($1, $2, $3, $4)",
            saad_id, "saad", "saadjamalsaifi@gmail.com", "$2b$12$oYqUsOKiFQD1osgW6lAPC.bwStMDnkEO4M8yVsyjYvWW7SrY.jUgW"
        )
    else:
        saad_id = saad_user["userid"]

    if not john_user:
        john_id = uuid.uuid4()
        await conn.execute(
            "INSERT INTO users (userid, name, email, password) VALUES ($1, $2, $3, $4)",
            john_id, "John Doe", "devayush402@gmail.com", "$2b$12$oYqUsOKiFQD1osgW6lAPC.bwStMDnkEO4M8yVsyjYvWW7SrY.jUgW"
        )
    else:
        john_id = john_user["userid"]
        await conn.execute("UPDATE users SET name = 'John Doe' WHERE userid = $1", john_id)

    user_ids = [saad_id, john_id]
    print(f"Target Users -> saad: {saad_id}, John Doe: {john_id}")

    async with conn.transaction():
        # Clear existing data for target users
        for uid in user_ids:
            await conn.execute("DELETE FROM inventory_alerts WHERE userid = $1", uid)
            await conn.execute("DELETE FROM orders WHERE userid = $1", uid)
            await conn.execute("DELETE FROM products WHERE userid = $1", uid)
            await conn.execute("DELETE FROM stores WHERE userid = $1", uid)
            await conn.execute("DELETE FROM dashboard_summary WHERE userid = $1", uid)

        print("Cleaned existing data for target users.")

        for uid in user_ids:
            user_label = "saad" if uid == saad_id else "John Doe"
            print(f"\nBuilding seed batch for {user_label}...")

            # --- STORES (5 stores) ---
            stores_batch = []
            store_ids = []
            selected_platforms = random.sample(STORE_PLATFORMS, 5)
            for platform, country in selected_platforms:
                sid = uuid.uuid4()
                store_ids.append(sid)
                stores_batch.append((sid, uid, platform, country, "connected"))

            await conn.executemany(
                "INSERT INTO stores (storeid, userid, platform, country, status) VALUES ($1, $2, $3, $4, $5)",
                stores_batch
            )
            print(f"  Inserted 5 stores.")

            # --- PRODUCTS (50 products) ---
            products_batch = []
            product_ids = []
            total_revenue = 0.0
            total_units_sold = 0

            shuffled_names = list(PRODUCT_NAMES)
            random.shuffle(shuffled_names)

            for i in range(50):
                pid = uuid.uuid4()
                product_ids.append(pid)
                assigned_store = store_ids[i % len(store_ids)]
                pname = shuffled_names[i] if i < len(shuffled_names) else f"Product #{i+1} Special"
                
                units = random.randint(25, 450)
                unit_price = round(random.uniform(15.00, 180.00), 2)
                rev = round(units * unit_price, 2)
                
                total_units_sold += units
                total_revenue += rev

                products_batch.append((pid, uid, assigned_store, pname, units, rev))

            await conn.executemany(
                "INSERT INTO products (productid, userid, storeid, product_name, units_sold, revenue) VALUES ($1, $2, $3, $4, $5, $6)",
                products_batch
            )
            print(f"  Inserted 50 products.")

            # --- ORDERS (35 orders) ---
            orders_batch = []
            order_count = 35
            for _ in range(order_count):
                oid = uuid.uuid4()
                assigned_store = random.choice(store_ids)
                c_name = random.choice(CUSTOMER_NAMES)
                c_email = c_name.lower().replace(" ", ".").replace("'", "") + "@example.com"
                amount = round(random.uniform(30.00, 250.00), 2)
                status = random.choice(STATUSES)
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

                orders_batch.append((oid, uid, assigned_store, c_name, c_email, amount, status, created_at))

            await conn.executemany(
                "INSERT INTO orders (orderid, userid, storeid, customer_name, customer_email, amount, status, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                orders_batch
            )
            print(f"  Inserted 35 orders.")

            # --- INVENTORY ALERTS (10 alerts) ---
            alerts_batch = []
            alert_products = random.sample(product_ids, 10)
            for idx, pid in enumerate(alert_products):
                aid = uuid.uuid4()
                stock = 0 if idx < 3 else random.randint(1, 15)
                alert_type = "Out of Stock" if stock == 0 else "Low Stock"
                alerts_batch.append((aid, uid, pid, stock, alert_type))

            await conn.executemany(
                "INSERT INTO inventory_alerts (alert_id, userid, productid, stock, alert_type) VALUES ($1, $2, $3, $4, $5)",
                alerts_batch
            )
            print(f"  Inserted 10 inventory alerts.")

            # --- DASHBOARD SUMMARY ---
            summary_id = uuid.uuid4()
            refunds = round(total_revenue * 0.02, 2)
            profit = round(total_revenue * 0.35, 2)
            aov = round(total_revenue / max(1, total_units_sold), 2)

            await conn.execute(
                """
                INSERT INTO dashboard_summary (summaryid, userid, revenue, orders, units_sold, refunds, profit, average_order_value)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                summary_id, uid, round(total_revenue, 2), order_count, total_units_sold, refunds, profit, aov
            )
            print(f"  Inserted dashboard summary: Revenue=${total_revenue:,.2f}, Orders={order_count}, Units={total_units_sold}.")

    await conn.close()
    print("\n✅ All seed data inserted in fast bulk mode!")

if __name__ == "__main__":
    asyncio.run(seed())
