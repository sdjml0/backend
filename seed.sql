-- Enable pgcrypto extension for UUID generation if needed
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. TABLE CREATION SCHEMA
-- ============================================================================

DROP TABLE IF EXISTS inventory_alerts CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
DROP TABLE IF EXISTS dashboard_summary CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users Table
CREATE TABLE users (
    userid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    postalcode VARCHAR(20),
    country VARCHAR(100),
    password VARCHAR(255) NOT NULL
);

-- Dashboard Summary Table
CREATE TABLE dashboard_summary (
    summaryid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userid UUID UNIQUE REFERENCES users(userid) ON DELETE CASCADE,
    revenue NUMERIC(12, 2) DEFAULT 0.00,
    orders INT DEFAULT 0,
    units_sold INT DEFAULT 0,
    refunds NUMERIC(12, 2) DEFAULT 0.00,
    profit NUMERIC(12, 2) DEFAULT 0.00,
    average_order_value NUMERIC(12, 2) DEFAULT 0.00
);

-- Stores Table
CREATE TABLE stores (
    storeid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userid UUID REFERENCES users(userid) ON DELETE CASCADE,
    platform VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    status VARCHAR(50) DEFAULT 'connected'
);

-- Products Table
CREATE TABLE products (
    productid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userid UUID REFERENCES users(userid) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    units_sold INT DEFAULT 0,
    revenue NUMERIC(12, 2) DEFAULT 0.00
);

-- Orders Table
CREATE TABLE orders (
    orderid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userid UUID REFERENCES users(userid) ON DELETE CASCADE,
    storeid UUID REFERENCES stores(storeid) ON DELETE SET NULL,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Alerts Table
CREATE TABLE inventory_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userid UUID REFERENCES users(userid) ON DELETE CASCADE,
    productid UUID REFERENCES products(productid) ON DELETE CASCADE,
    stock INT NOT NULL,
    alert_type VARCHAR(50) NOT NULL
);


-- ============================================================================
-- 2. SEED DATA FOR SPECIFIC USER ID: 5d09522b-a187-46bc-bf57-2c9b4407dddf
-- ============================================================================

-- Primary User (userid: '5d09522b-a187-46bc-bf57-2c9b4407dddf')
INSERT INTO users (userid, name, email, phone, address, city, postalcode, country, password)
VALUES 
    ('5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Alex Morgan', 'alex.morgan@example.com', '+1 555-0198', '123 Commerce St', 'San Francisco', '94105', 'United States', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'Priya Sharma', 'priya.sharma@example.com', '+91 9876543210', '45 MG Road', 'Bangalore', '560001', 'India', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'David Miller', 'david.miller@example.com', '+44 20 7946 0912', '88 Baker St', 'London', 'NW1 6XE', 'United Kingdom', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'Sarah Jenkins', 'sarah.jenkins@example.com', '+1 555-0144', '742 Evergreen Terrace', 'Springfield', '97477', 'United States', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'Michael Chen', 'michael.chen@example.com', '+1 555-0177', '500 Market St', 'Seattle', '98101', 'United States', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'Elena Rostova', 'elena.rostova@example.com', '+49 30 123456', 'Kurfürstendamm 21', 'Berlin', '10719', 'Germany', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a17', 'Kenji Sato', 'kenji.sato@example.com', '+81 3 1234 5678', '1-2-3 Ginza', 'Tokyo', '104-0061', 'Japan', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a18', 'Lucas Silva', 'lucas.silva@example.com', '+55 11 98765-4321', 'Av. Paulista 1000', 'São Paulo', '01310-100', 'Brazil', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a19', 'Chloe Dubois', 'chloe.dubois@example.com', '+33 1 42 68 55 00', '15 Rue de Rivoli', 'Paris', '75004', 'France', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 'Liam O''Connor', 'liam.oconnor@example.com', '+61 2 9374 4000', '200 George St', 'Sydney', '2000', 'Australia', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW');

-- Dashboard Summary for User 5d09522b-a187-46bc-bf57-2c9b4407dddf
INSERT INTO dashboard_summary (summaryid, userid, revenue, orders, units_sold, refunds, profit, average_order_value)
VALUES 
    ('f1111111-1111-1111-1111-111111111111', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 125430.50, 2845, 4982, 2345.60, 25430.80, 44.08);

-- 10 Connected Stores for User 5d09522b-a187-46bc-bf57-2c9b4407dddf
INSERT INTO stores (storeid, userid, platform, country, status)
VALUES 
    ('b1111111-1111-1111-1111-111111111111', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Amazon', 'United States', 'connected'),
    ('b2222222-2222-2222-2222-222222222222', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Flipkart', 'India', 'connected'),
    ('b3333333-3333-3333-3333-333333333333', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'eBay', 'Global', 'connected'),
    ('b4444444-4444-4444-4444-444444444444', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Shopify', 'My Store', 'connected'),
    ('b5555555-5555-5555-5555-555555555555', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'WooCommerce', 'My Website', 'connected'),
    ('b6666666-6666-6666-6666-666666666666', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Etsy', 'United States', 'connected'),
    ('b7777777-7777-7777-7777-777777777777', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Walmart', 'United States', 'connected'),
    ('b8888888-8888-8888-8888-888888888888', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Rakuten', 'Japan', 'connected'),
    ('b9999999-9999-9999-9999-999999999999', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Mercado Libre', 'Brazil', 'connected'),
    ('b0000000-0000-0000-0000-000000000000', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Alibaba', 'Global', 'connected');

-- 10 Products for User 5d09522b-a187-46bc-bf57-2c9b4407dddf
INSERT INTO products (productid, userid, product_name, units_sold, revenue)
VALUES 
    ('c1111111-1111-1111-1111-111111111111', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Noise Cancelling Headphones', 1245, 18742.50),
    ('c2222222-2222-2222-2222-222222222222', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Smart Watch Series 8', 892, 16280.00),
    ('c3333333-3333-3333-3333-333333333333', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Wireless Earbuds', 1032, 12910.30),
    ('c4444444-4444-4444-4444-444444444444', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Portable Bluetooth Speaker', 645, 7680.20),
    ('c5555555-5555-5555-5555-555555555555', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Phone Charger 20W', 1168, 5326.40),
    ('c6666666-6666-6666-6666-666666666666', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Mechanical Gaming Keyboard', 520, 8900.00),
    ('c7777777-7777-7777-7777-777777777777', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'Wireless Ergonomic Mouse', 780, 4680.00),
    ('c8888888-8888-8888-8888-888888888888', '5d09522b-a187-46bc-bf57-2c9b4407dddf', '4K Ultra HD Monitor 27"', 310, 11470.00),
    ('c9999999-9999-9999-9999-999999999999', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'USB-C Multiport Docking Hub', 940, 6580.00),
    ('c0000000-0000-0000-0000-000000000000', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'HD Webcam 1080p Auto-Focus', 610, 4270.00);

-- 10 Orders for User 5d09522b-a187-46bc-bf57-2c9b4407dddf
INSERT INTO orders (orderid, userid, storeid, customer_name, customer_email, amount, status, created_at)
VALUES 
    ('d1111111-1111-1111-1111-111111111111', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b1111111-1111-1111-1111-111111111111', 'Alex Morgan', 'alex@example.com', 95.80, 'Delivered', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    ('d2222222-2222-2222-2222-222222222222', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b2222222-2222-2222-2222-222222222222', 'Priya Sharma', 'priya@example.com', 42.30, 'Processing', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
    ('d3333333-3333-3333-3333-333333333333', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b3333333-3333-3333-3333-333333333333', 'David Miller', 'david@example.com', 129.99, 'Shipped', CURRENT_TIMESTAMP - INTERVAL '5 hours'),
    ('d4444444-4444-4444-4444-444444444444', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b4444444-4444-4444-4444-444444444444', 'Sarah Jenkins', 'sarah@example.com', 59.00, 'Delivered', CURRENT_TIMESTAMP - INTERVAL '8 hours'),
    ('d5555555-5555-5555-5555-555555555555', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b1111111-1111-1111-1111-111111111111', 'Michael Chen', 'michael@example.com', 89.50, 'Cancelled', CURRENT_TIMESTAMP - INTERVAL '12 hours'),
    ('d6666666-6666-6666-6666-666666666666', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b5555555-5555-5555-5555-555555555555', 'Elena Rostova', 'elena@example.com', 145.20, 'Delivered', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('d7777777-7777-7777-7777-777777777777', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b6666666-6666-6666-6666-666666666666', 'Kenji Sato', 'kenji@example.com', 38.00, 'Processing', CURRENT_TIMESTAMP - INTERVAL '1 day 4 hours'),
    ('d8888888-8888-8888-8888-888888888888', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b7777777-7777-7777-7777-777777777777', 'Lucas Silva', 'lucas@example.com', 210.00, 'Shipped', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('d9999999-9999-9999-9999-999999999999', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b8888888-8888-8888-8888-888888888888', 'Chloe Dubois', 'chloe@example.com', 75.40, 'Delivered', CURRENT_TIMESTAMP - INTERVAL '2 days 6 hours'),
    ('d0000000-0000-0000-0000-000000000000', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'b9999999-9999-9999-9999-999999999999', 'Liam O''Connor', 'liam@example.com', 115.00, 'Processing', CURRENT_TIMESTAMP - INTERVAL '3 days');

-- 10 Inventory Alerts for User 5d09522b-a187-46bc-bf57-2c9b4407dddf
INSERT INTO inventory_alerts (alert_id, userid, productid, stock, alert_type)
VALUES 
    ('e1111111-1111-1111-1111-111111111111', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c3333333-3333-3333-3333-333333333333', 15, 'Low Stock'),
    ('e2222222-2222-2222-2222-222222222222', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c2222222-2222-2222-2222-222222222222', 8, 'Low Stock'),
    ('e3333333-3333-3333-3333-333333333333', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c4444444-4444-4444-4444-444444444444', 12, 'Low Stock'),
    ('e4444444-4444-4444-4444-444444444444', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c5555555-5555-5555-5555-555555555555', 9, 'Low Stock'),
    ('e5555555-5555-5555-5555-555555555555', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c6666666-6666-6666-6666-666666666666', 3, 'Low Stock'),
    ('e6666666-6666-6666-6666-666666666666', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c7777777-7777-7777-7777-777777777777', 0, 'Out of Stock'),
    ('e7777777-7777-7777-7777-777777777777', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c8888888-8888-8888-8888-888888888888', 5, 'Low Stock'),
    ('e8888888-8888-8888-8888-888888888888', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c9999999-9999-9999-9999-999999999999', 14, 'Low Stock'),
    ('e9999999-9999-9999-9999-999999999999', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c0000000-0000-0000-0000-000000000000', 0, 'Out of Stock'),
    ('e0000000-0000-0000-0000-000000000000', '5d09522b-a187-46bc-bf57-2c9b4407dddf', 'c1111111-1111-1111-1111-111111111111', 18, 'Low Stock');
