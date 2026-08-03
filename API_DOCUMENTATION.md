# E-Commerce API Documentation

Complete, authoritative API Reference for Authentication, User Profile Management, Product CRUD, Store Management, E-Commerce Dashboard Analytics, Database Schema, and Error Specifications.

---

## 1. Overview & Architecture

- **Base URL**: `http://localhost:8000` (Local) / `https://ecom-1-0.onrender.com` (Production)
- **Interactive Documentation**: `/docs` (Swagger UI) or `/redoc`
- **Authentication Standard**: HTTP Bearer JWT Tokens (`Authorization: Bearer <accessToken>`)
- **Modular Feature Architecture**:
  - `features/auth/` — Signup, Login, Password Reset, User Profile CRUD & Aliases
  - `features/otp/` — Magic Link & 6-Digit Email OTP Generation & Verification
  - `features/products/` — Full Product Management CRUD with Single-Query Window Function Pagination
  - `features/stores/` — Connected Marketplace Store CRUD & Store Product Association
  - `features/dashboard/` — Aggregated E-Commerce Analytics, Orders, and Inventory Metrics

---

## 2. Environment Configuration

| Key | Description | Example / Default Value |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL Connection DSN | `postgresql://user:pass@host/neondb?sslmode=require` |
| `SECRET_KEY` | JWT signing secret key | `ThisIsMySecretKeyChangeInProduction` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity (minutes) | `60` |
| `OTP_EXPIRE_MINUTES` | OTP / Magic link code validity (minutes) | `10` |
| `BREVO_API_KEY` | Brevo (Sendinblue) transactional email API key | `xkeysib-...` |
| `BREVO_SENDER_EMAIL` | Verified Brevo sender email | `your-email@example.com` |
| `SMTP_HOST` | SMTP fallback server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `USERNAME_GMAIL_SMTP` | SMTP username | `your-email@gmail.com` |
| `PASSWORD_GMAIL_SMTP` | SMTP app password | `xxxx xxxx xxxx xxxx` |
| `EMAILS_FROM_NAME` | Sender name shown in inbox | `E-Commerce Admin` |

---

## 3. Authentication & User Management API

All endpoints except `/auth/signup`, `/auth/login`, `/auth/forgot-password`, `/auth/send-magic-link`, `/auth/verify-link`, and `/auth/reset-password` require `Authorization: Bearer <accessToken>`.

---

### 3.1 Step 1: Submit Registration Details & Request Email Verification
- **URL**: `POST /auth/signup`
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "name": "Alex Morgan",
  "email": "alex.morgan@example.com",
  "password": "SecretPassword123",
  "phone": "+1 555-0198",
  "address": "123 Commerce St",
  "city": "San Francisco",
  "postalcode": "94105",
  "country": "United States"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Registration details received. 6-digit OTP code sent to alex.morgan@example.com. Please verify OTP to complete account creation.",
  "email": "alex.morgan@example.com",
  "expires_in_minutes": 10
}
```

---

### 3.2 Request Forgot Password Reset Link
- **URL**: `POST /auth/forgot-password` *(Alias: `POST /auth/forgotpassword`)*
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "email": "alex.morgan@example.com"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Magic link sent to alex.morgan@example.com. It will expire in 10 minutes.",
  "expires_in_minutes": 10
}
```

---

### 3.3 Request Magic Link Email (General / Signup / Reset)
- **URL**: `POST /auth/send-magic-link` *(Alias: `POST /auth/send-otp`)*
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "email": "alex.morgan@example.com",
  "purpose": "signup"
}
```
*(If `purpose` is omitted, automatically checks if user exists: sets `password_reset` if user exists, or `signup` if new user)*

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Magic link sent to alex.morgan@example.com. It will expire in 10 minutes.",
  "expires_in_minutes": 10
}
```

---

### 3.4 Verify Magic Link Token (Email Link Click & Auto-Login)
- **URL**: `GET /auth/verify-link?token=k9X_mP2zQ7vW0xY1zA3bC5dE7fG9hI1jK3mL5nO7pQ9&email=alex.morgan%40example.com`
- **Supported Query Aliases**: `?token=...`, `?resetotp=...`, `?otp=...`, `?code=...`, `?email=...`
- **Headers**: None

#### Response (`200 OK` - Signup Verification & Instant Auto-Login):
```json
{
  "message": "User registered successfully.",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "email": "alex.morgan@example.com",
  "accessToken": "eyJhbGciOiJIUzI1Ni...",
  "expiresIn": 3600,
  "user": {
    "id": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
    "name": "Alex Morgan",
    "email": "alex.morgan@example.com",
    "role": "Owner"
  }
}
```

#### Response (`200 OK` - Password Reset Token Validation):
```json
{
  "success": true,
  "message": "Magic link token validated successfully.",
  "purpose": "password_reset",
  "email": "alex.morgan@example.com"
}
```

---

### 3.5 Reset Password & Auto-Login
- **URL**: `POST /auth/reset-password` *(Alias: `POST /auth/resetpassword`)*
- **Headers**: `Content-Type: application/json`

#### Supported Payload Parameter Aliases:
- Token parameter can be sent as: `token`, `resetotp`, `otp`, or `code`.
- Password parameter can be sent as: `new_password`, `password`, or `newPassword`.

#### Request Payload:
```json
{
  "token": "k9X_mP2zQ7vW0xY1zA3bC5dE7fG9hI1jK3mL5nO7pQ9",
  "new_password": "NewSecretPassword456"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Password updated successfully. You are now logged in.",
  "accessToken": "eyJhbGciOiJIUzI1Ni...",
  "expiresIn": 3600,
  "user": {
    "id": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
    "name": "Alex Morgan",
    "email": "alex.morgan@example.com",
    "role": "Owner"
  }
}
```

---

### 3.6 User Login
- **URL**: `POST /auth/login`
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "email": "alex.morgan@example.com",
  "password": "SecretPassword123"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "accessToken": "eyJhbGciOiJIUzI1Ni...",
  "expiresIn": 3600,
  "user": {
    "id": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
    "name": "Alex Morgan",
    "email": "alex.morgan@example.com",
    "role": "Owner"
  }
}
```

---

### 3.7 Get Authenticated User Profile
- **URL**: `GET /auth/me` *(Alias: `GET /auth/profile`)*
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "name": "Alex Morgan",
  "email": "alex.morgan@example.com",
  "phone": "+1 555-0198",
  "address": "123 Commerce St",
  "city": "San Francisco",
  "postalcode": "94105",
  "country": "United States"
}
```

---

### 3.8 Update Authenticated User Profile
- **URL**: `PUT /auth/me` or `PATCH /auth/me` *(Aliases: `PUT /auth/profile`, `PATCH /auth/profile`)*
- **Headers**: `Authorization: Bearer <accessToken>`, `Content-Type: application/json`

#### Supported Postal Code Parameter Aliases:
Accepts `postalcode`, `postal_code`, `postalCode`, `zip`, or `zipcode`.

#### Request Payload (Partial updates supported):
```json
{
  "name": "Alex Morgan",
  "phone": "+1 555-9988",
  "address": "456 Market St, Suite 200",
  "city": "San Francisco",
  "postal_code": "94105",
  "country": "United States"
}
```

#### Response (`200 OK`):
```json
{
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "name": "Alex Morgan",
  "email": "alex.morgan@example.com",
  "phone": "+1 555-9988",
  "address": "456 Market St, Suite 200",
  "city": "San Francisco",
  "postalcode": "94105",
  "country": "United States"
}
```

---

### 3.9 Delete User Account
- **URL**: `DELETE /auth/me`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "User account successfully deleted."
}
```

---

## 4. Product Management CRUD API

All product endpoints require `Authorization: Bearer <accessToken>`.

---

### 4.1 Create Product
- **URL**: `POST /v1/products`
- **Headers**: `Authorization: Bearer <accessToken>`, `Content-Type: application/json`

#### Request Payload:
```json
{
  "product_name": "Wireless Ergonomic Mouse",
  "storeid": "b1111111-1111-1111-1111-111111111111",
  "units_sold": 150,
  "revenue": 4498.50
}
```

#### Response (`201 Created`):
```json
{
  "productid": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a99",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "storeid": "b1111111-1111-1111-1111-111111111111",
  "product_name": "Wireless Ergonomic Mouse",
  "units_sold": 150,
  "revenue": 4498.50
}
```

---

### 4.2 List Products (With Pagination & Store Filtering)
- **URL**: `GET /v1/products`
- **Query Parameters**:
  - `page` (int, default `1`): Current page number (1-indexed)
  - `page_size` (int, default `10`, max `100`): Items per page
  - `storeid` / `store_id` (UUID, optional): Filter products by store ID
  - `limit` (int, optional): Legacy offset limit
  - `offset` (int, optional): Legacy skip offset
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "success": true,
  "total": 24,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false,
  "count": 10,
  "data": [
    {
      "productid": "c1111111-1111-1111-1111-111111111111",
      "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
      "storeid": "b1111111-1111-1111-1111-111111111111",
      "product_name": "Noise Cancelling Headphones",
      "units_sold": 1245,
      "revenue": 18742.50
    },
    {
      "productid": "c2222222-2222-2222-2222-222222222222",
      "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
      "storeid": "b1111111-1111-1111-1111-111111111111",
      "product_name": "Smart Watch Series 8",
      "units_sold": 892,
      "revenue": 16280.00
    }
  ]
}
```

---

### 4.3 List Products by Specific Store
- **URL**: `GET /v1/products/store/{storeid}?page=1&page_size=10`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
Returns the same `ProductListResponse` schema filtered to `{storeid}`.

---

### 4.4 Get Product by ID
- **URL**: `GET /v1/products/{productid}`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "productid": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a99",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "storeid": "b1111111-1111-1111-1111-111111111111",
  "product_name": "Wireless Ergonomic Mouse",
  "units_sold": 150,
  "revenue": 4498.50
}
```

---

### 4.5 Update Product
- **URL**: `PUT /v1/products/{productid}`
- **Headers**: `Authorization: Bearer <accessToken>`, `Content-Type: application/json`

#### Request Payload:
```json
{
  "product_name": "Wireless Ergonomic Mouse v2",
  "revenue": 5998.00
}
```

#### Response (`200 OK`):
```json
{
  "productid": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a99",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "storeid": "b1111111-1111-1111-1111-111111111111",
  "product_name": "Wireless Ergonomic Mouse v2",
  "units_sold": 150,
  "revenue": 5998.00
}
```

---

### 4.6 Delete Product
- **URL**: `DELETE /v1/products/{productid}`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Product 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a99' successfully deleted."
}
```

---

## 5. Store Management CRUD API

All store endpoints require `Authorization: Bearer <accessToken>`.

---

### 5.1 Connect / Create Store
- **URL**: `POST /v1/stores`
- **Headers**: `Authorization: Bearer <accessToken>`, `Content-Type: application/json`

#### Request Payload:
```json
{
  "platform": "Shopify",
  "country": "United States",
  "status": "connected"
}
```

#### Response (`201 Created`):
```json
{
  "storeid": "c11ebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "platform": "Shopify",
  "country": "United States",
  "status": "connected"
}
```

---

### 5.2 List Connected Stores
- **URL**: `GET /v1/stores` *(Query params: `limit=50`, `offset=0`)*
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "storeid": "c11ebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
      "platform": "Shopify",
      "country": "United States",
      "status": "connected"
    }
  ]
}
```

---

### 5.3 Get Store Details by ID
- **URL**: `GET /v1/stores/{storeid}`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "storeid": "c11ebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "platform": "Shopify",
  "country": "United States",
  "status": "connected"
}
```

---

### 5.4 Get Products Belongs to Store
- **URL**: `GET /v1/stores/{storeid}/products?page=1&page_size=10`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
Returns standard `ProductListResponse` schema for `{storeid}`.

---

### 5.5 Update Store Status / Details
- **URL**: `PUT /v1/stores/{storeid}`
- **Headers**: `Authorization: Bearer <accessToken>`, `Content-Type: application/json`

#### Request Payload:
```json
{
  "status": "syncing"
}
```

#### Response (`200 OK`):
```json
{
  "storeid": "c11ebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "platform": "Shopify",
  "country": "United States",
  "status": "syncing"
}
```

---

### 5.6 Disconnect / Delete Store
- **URL**: `DELETE /v1/stores/{storeid}`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Store 'c11ebc99-9c0b-4ef8-bb6d-6bb9bd380a11' successfully deleted."
}
```

---

## 6. Dashboard & Analytics API

All dashboard endpoints require `Authorization: Bearer <accessToken>`.

---

### 6.1 Aggregated Dashboard Overview
- **URL**: `GET /v1/dashboard/overview` *(Alias: `GET /dashboard`)*
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "status": "success",
  "data": {
    "connectedStores": [
      {
        "id": "store-1",
        "name": "Amazon",
        "displayName": "Amazon",
        "country": "United States",
        "status": "connected",
        "revenue": "$44,620.80",
        "logoText": "a",
        "brandColor": "#0F4C81"
      }
    ],
    "kpiMetrics": [
      {
        "id": "metric-revenue",
        "title": "Total Revenue",
        "value": "$125,430.50",
        "change": "18.5%",
        "isPositive": true,
        "comparisonPeriod": "vs last 7 days",
        "iconName": "DollarSign",
        "color": "#0F4C81",
        "sparkline": [{ "val": 120 }, { "val": 135 }, { "val": 170 }]
      }
    ],
    "revenueAnalytics": [
      {
        "date": "Mon",
        "Amazon": 6200,
        "Flipkart": 4100,
        "Shopify": 3400,
        "total": 13700
      }
    ],
    "marketplaceShares": [
      {
        "name": "Amazon",
        "percentage": 35.6,
        "revenue": "$44,620.80",
        "color": "#0F4C81"
      }
    ],
    "orderStatusShares": [
      {
        "name": "Delivered",
        "count": 1845,
        "percentage": 64.8,
        "color": "#22C55E"
      }
    ],
    "recentOrders": [
      {
        "id": "ord-101",
        "orderNumber": "#ORD-9842",
        "customerName": "Sarah Jenkins",
        "customerEmail": "sarah.j@example.com",
        "marketplace": "Amazon",
        "date": "10 mins ago",
        "amount": "$249.99",
        "status": "Delivered"
      }
    ],
    "topProducts": [
      {
        "id": "prod-1",
        "name": "Noise Cancelling Headphones",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100&q=80",
        "unitsSold": 1245,
        "revenue": "$18,742.50"
      }
    ],
    "inventoryAlerts": [
      {
        "id": "inv-1",
        "name": "Ergonomic Wireless Mouse",
        "sku": "MS-ERG-001",
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=100&q=80",
        "stockLeft": 4,
        "status": "Low Stock"
      }
    ]
  }
}
```

---

### 6.2 Key Analytics Breakdown Endpoints

| Method | URL | Description | Response Schema |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/metrics/kpi` | KPI metric cards with sparkline trend points | `List[MetricDataDTO]` |
| `GET` | `/v1/analytics/revenue` | Revenue breakdown grouped by day & marketplace | `List[RevenueDataPointDTO]` |
| `GET` | `/v1/analytics/marketplace-share` | Revenue percentage share by platform | `List[MarketplaceShareDTO]` |
| `GET` | `/v1/orders` | Full list of user orders | `List[RecentOrderDTO]` |
| `GET` | `/v1/orders/recent` | 10 most recent orders | `List[RecentOrderDTO]` |
| `GET` | `/v1/products/analytics` | Product list for analytics overview | `List[TopProductDTO]` |
| `GET` | `/v1/products/top-selling` | Top selling product rankings | `List[TopProductDTO]` |
| `GET` | `/v1/inventory` | Inventory items stock status list | `List[InventoryAlertDTO]` |
| `GET` | `/v1/inventory/alerts` | Low stock and out-of-stock inventory alerts | `List[InventoryAlertDTO]` |
| `GET` | `/` | API status health check | `{"message": "...", "version": "1.0.0"}` |

---

## 7. Database Schema & Data Models

The API connects to PostgreSQL using the following schema (defined in `seed.sql`):

- **`users`**:
  - `userid` (UUID, Primary Key)
  - `name` (VARCHAR)
  - `email` (VARCHAR, Unique)
  - `phone`, `address`, `city`, `postalcode`, `country` (VARCHAR/TEXT)
  - `password` (VARCHAR, Hashed)

- **`stores`**:
  - `storeid` (UUID, Primary Key)
  - `userid` (UUID, Foreign Key -> `users.userid` ON DELETE CASCADE)
  - `platform` (VARCHAR - e.g., Amazon, Shopify, Flipkart)
  - `country` (VARCHAR)
  - `status` (VARCHAR - e.g., connected, syncing, disconnected)

- **`products`**:
  - `productid` (UUID, Primary Key)
  - `userid` (UUID, Foreign Key -> `users.userid` ON DELETE CASCADE)
  - `storeid` (UUID, Foreign Key -> `stores.storeid` ON DELETE SET NULL)
  - `product_name` (VARCHAR)
  - `units_sold` (INT)
  - `revenue` (NUMERIC 12,2)

- **`orders`**:
  - `orderid` (UUID, Primary Key)
  - `userid` (UUID, Foreign Key -> `users.userid` ON DELETE CASCADE)
  - `storeid` (UUID, Foreign Key -> `stores.storeid` ON DELETE SET NULL)
  - `customer_name`, `customer_email` (VARCHAR)
  - `amount` (NUMERIC 12,2)
  - `status` (VARCHAR - e.g., Delivered, Shipped, Processing)
  - `created_at` (TIMESTAMP)

- **`inventory_alerts`**:
  - `alert_id` (UUID, Primary Key)
  - `userid` (UUID, Foreign Key -> `users.userid` ON DELETE CASCADE)
  - `productid` (UUID, Foreign Key -> `products.productid` ON DELETE CASCADE)
  - `stock` (INT)
  - `alert_type` (VARCHAR - e.g., Low Stock, Out of Stock)

- **`dashboard_summary`**:
  - `summaryid` (UUID, Primary Key)
  - `userid` (UUID, Foreign Key -> `users.userid` ON DELETE CASCADE)
  - `revenue`, `orders`, `units_sold`, `refunds`, `profit`, `average_order_value`

---

## 8. Error Handling & Standard Responses

All error responses return standard JSON structures with appropriate HTTP status codes:

- **400 Bad Request**: Invalid inputs or business logic violation.
  ```json
  {
    "detail": "Email already registered."
  }
  ```
- **401 Unauthorized**: Missing or expired Bearer token.
  ```json
  {
    "detail": "Invalid authorization credentials."
  }
  ```
- **404 Not Found**: Resource does not exist or user does not have permission to view it.
  ```json
  {
    "detail": "Product not found."
  }
  ```
- **422 Unprocessable Entity**: Request body validation failure (Pydantic schema).
  ```json
  {
    "detail": [
      {
        "loc": ["body", "email"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

---

## 9. cURL Quickstart Examples

### Login & Get Bearer Token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "alex.morgan@example.com", "password": "SecretPassword123"}'
```

### Fetch Authenticated User Profile:
```bash
curl -X GET "http://localhost:8000/auth/me" \
     -H "Authorization: Bearer <accessToken>"
```

### Fetch Paginated Products:
```bash
curl -X GET "http://localhost:8000/v1/products?page=1&page_size=10" \
     -H "Authorization: Bearer <accessToken>"
```

### Fetch Aggregated Dashboard Overview:
```bash
curl -X GET "http://localhost:8000/v1/dashboard/overview" \
     -H "Authorization: Bearer <accessToken>"
```
