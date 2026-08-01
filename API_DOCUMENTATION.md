# E-Commerce API Documentation

Complete API Reference for Authentication, User Profile Management, Product CRUD, Store CRUD, and E-Commerce Dashboard Analytics.

---

## 1. Overview & Architecture

- **Base URL**: `http://localhost:8000` (Local) / `https://<your-app>.onrender.com` (Production)
- **Interactive Documentation**: `/docs` (Swagger UI) or `/redoc`
- **Authentication Standard**: HTTP Bearer JWT Tokens (`Authorization: Bearer <accessToken>`)
- **Modular Feature Architecture**:
  - `features/auth/` — Signup, Login, Password Reset, User Profile CRUD
  - `features/otp/` — 6-Digit Email OTP Generation & Verification
  - `features/products/` — Full Product Management CRUD
  - `features/stores/` — Connected Marketplace Store CRUD
  - `features/dashboard/` — Aggregated E-Commerce Analytics & Reports

---

## 2. Environment Configuration

| Key | Description | Example / Default Value |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL Connection DSN | `postgresql://user:pass@host/neondb?sslmode=require` |
| `SECRET_KEY` | JWT signing secret key | `ThisIsMySecretKeyChangeInProduction` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity (minutes) | `60` |
| `OTP_EXPIRE_MINUTES` | OTP code validity (minutes) | `10` |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `USERNAME_GMAIL_SMTP` | SMTP username | `your-email@gmail.com` |
| `PASSWORD_GMAIL_SMTP` | SMTP app password | `xxxx xxxx xxxx xxxx` |
| `EMAILS_FROM_NAME` | Sender name shown in inbox | `E-Commerce Security` |

---

## 3. Authentication & User Management API

All `/auth/me` profile management endpoints require `Authorization: Bearer <accessToken>`.

### 3.1 Step 1: Submit Registration Details & Request OTP
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

### 3.3 Request Magic Link Email (General / Signup)
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

### 3.4 Verify Magic Link Token (Email Link Click)
- **URL**: `GET /auth/verify-link?token=k9X_mP2zQ7vW0xY1zA3bC5dE7fG9hI1jK3mL5nO7pQ9` *(Supports `?token=...`, `?resetotp=...`, `?otp=...`, `?code=...`)*
- **Headers**: None

#### Response (`200 OK` - Signup Verification & Auto-Login):
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

#### Request Payload:
```json
{
  "email": "alex.morgan@example.com",
  "token": "k9X_mP2zQ7vW0xY1zA3bC5dE7fG9hI1jK3mL5nO7pQ9",
  "new_password": "NewSecretPassword456"
}
```
*(Field Aliases Supported: Token can be `token`, `resetotp`, `otp`, or `code`; Password can be `new_password`, `password`, or `newPassword`; `email` is optional)*

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

### 3.5 User Login
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

### 3.6 Get Authenticated User Profile
- **URL**: `GET /auth/me`
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

### 3.7 Update Authenticated User Profile
- **URL**: `PUT /auth/me`
- **Headers**: `Authorization: Bearer <accessToken>`, `Content-Type: application/json`

#### Request Payload (Partial update allowed):
```json
{
  "phone": "+1 555-9988",
  "address": "456 Market St, Suite 200",
  "city": "San Francisco"
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

### 3.8 Delete User Account
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

All product CRUD endpoints require `Authorization: Bearer <accessToken>`.

### 4.1 Create Product
- **URL**: `POST /v1/products`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Request Payload:
```json
{
  "product_name": "Wireless Ergonomic Mouse",
  "units_sold": 150,
  "revenue": 4498.50
}
```

#### Response (`201 Created`):
```json
{
  "productid": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a99",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "product_name": "Wireless Ergonomic Mouse",
  "units_sold": 150,
  "revenue": 4498.50
}
```

---

### 4.2 List Products
- **URL**: `GET /v1/products?storeid=<store_uuid>&page=1&page_size=10` *(Supports `storeid`, `store_id`, `page`, `page_size`, `limit`, `offset`)*
- **Alias Endpoint**: `GET /v1/stores/{storeid}/products?page=1&page_size=10` or `GET /v1/products/store/{storeid}`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "success": true,
  "total": 2,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "has_next": false,
  "has_prev": false,
  "count": 2,
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

### 4.3 Get Product by ID
- **URL**: `GET /v1/products/{productid}`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "productid": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a99",
  "userid": "5d09522b-a187-46bc-bf57-2c9b4407dddf",
  "product_name": "Wireless Ergonomic Mouse",
  "units_sold": 150,
  "revenue": 4498.50
}
```

---

### 4.4 Update Product
- **URL**: `PUT /v1/products/{productid}`
- **Headers**: `Authorization: Bearer <accessToken>`

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
  "product_name": "Wireless Ergonomic Mouse v2",
  "units_sold": 150,
  "revenue": 5998.00
}
```

---

### 4.5 Delete Product
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

All store CRUD endpoints require `Authorization: Bearer <accessToken>`.

### 5.1 Connect / Create Store
- **URL**: `POST /v1/stores`
- **Headers**: `Authorization: Bearer <accessToken>`

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
- **URL**: `GET /v1/stores?limit=50&offset=0`
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

### 5.4 Update Store Details / Status
- **URL**: `PUT /v1/stores/{storeid}`
- **Headers**: `Authorization: Bearer <accessToken>`

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

### 5.5 Disconnect / Delete Store
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

### 6.1 Aggregated Dashboard Overview
- **URL**: `GET /v1/dashboard/overview` or `GET /dashboard`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "status": "success",
  "data": {
    "connectedStores": [...],
    "kpiMetrics": [...],
    "revenueAnalytics": [...],
    "marketplaceShares": [...],
    "orderStatusShares": [...],
    "recentOrders": [...],
    "topProducts": [...],
    "inventoryAlerts": [...]
  }
}
```

---

### 6.2 Key Analytics Breakdown Endpoints

| Method | URL | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/metrics/kpi` | Returns array of KPI metric summary cards with trend sparklines |
| `GET` | `/v1/analytics/revenue` | Time-series revenue breakdown grouped by platform |
| `GET` | `/v1/analytics/marketplace-share` | Revenue percentage share by marketplace platform |
| `GET` | `/v1/orders` | List of orders associated with the user |
| `GET` | `/v1/orders/recent` | List of 10 recent orders |
| `GET` | `/v1/products/analytics` | List of user products for dashboard display |
| `GET` | `/v1/products/top-selling` | Top selling product rankings |
| `GET` | `/v1/inventory` | Inventory stock status list |
| `GET` | `/v1/inventory/alerts` | Low stock and out-of-stock inventory alerts |
| `GET` | `/` | API status health check |
