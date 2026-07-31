# E-Commerce API Documentation

Complete reference documentation for Authentication, Email OTP Verification, and Password Reset APIs.

---

## 1. Overview & Architecture

- **Base URL**: `http://localhost:8000` (Local) / `https://<your-render-app>.onrender.com` (Production)
- **Interactive OpenAPI Docs**: `/docs` (Swagger UI) or `/redoc`
- **Authentication**: JWT Bearer Tokens (`Authorization: Bearer <token>`)
- **OTP System**:
  - **Code Format**: 6-digit numeric string (cryptographically secure random).
  - **Expiration**: 10 minutes (`expires_at = NOW() + 10 minutes`).
  - **Purposes**: `"signup"` and `"password_reset"`.
  - **Invalidation**: Requesting a new OTP automatically deletes previous unverified OTPs for that email and purpose.

---

## 2. Environment Variables Configuration

| Key | Description | Example / Recommended Value |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL Connection DSN | `postgresql://user:pass@ep-host.aws.neon.tech/neondb?sslmode=require` |
| `SECRET_KEY` | JWT signing secret key | `YourSuperSecretKeyGoesHere` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token validity in minutes | `60` |
| `OTP_EXPIRE_MINUTES` | OTP code validity in minutes | `10` |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP TLS port | `587` |
| `USERNAME_GMAIL_SMTP` | Gmail account for sending emails | `your-email@gmail.com` |
| `PASSWORD_GMAIL_SMTP` | Gmail 16-character App Password | `xxxx xxxx xxxx xxxx` |
| `EMAILS_FROM_EMAIL` | Sender email address | `your-email@gmail.com` |
| `EMAILS_FROM_NAME` | Sender name shown in recipient inbox | `E-Commerce Security` |

---

## 3. API Endpoints Reference

### 3.1 Send OTP

Generates a 6-digit OTP code and dispatches it via email to the client.

- **URL**: `POST /auth/send-otp`
- **Headers**: `Content-Type: application/json`

#### Request Payload (Sign Up OTP):
```json
{
  "email": "user@example.com",
  "purpose": "signup"
}
```

#### Request Payload (Password Reset OTP):
```json
{
  "email": "user@example.com",
  "purpose": "password_reset"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "6-digit OTP code sent to user@example.com. It will expire in 10 minutes.",
  "expires_in_minutes": 10
}
```

#### Error Responses:
- `409 Conflict`: If `purpose = "signup"` and the user email is already registered.
- `404 Not Found`: If `purpose = "password_reset"` and the user email is not found.

---

### 3.2 Verify OTP (Standalone Pre-Verification)

Optional endpoint to validate that a 6-digit OTP code is valid and active before submitting user forms.

- **URL**: `POST /auth/verify-otp`
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "purpose": "signup"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "OTP validated successfully.",
  "otpid": "d3d8039a-6d96-4e06-9a1e-234b47929d57"
}
```

#### Error Response (`400 Bad Request`):
```json
{
  "detail": "Invalid or expired 6-digit OTP code. Please request a new OTP."
}
```

---

### 3.3 User Sign Up (with Mandatory OTP)

Verifies the 6-digit OTP code, creates user credentials in PostgreSQL, and generates a JWT `accessToken` for immediate authentication.

- **URL**: `POST /auth/signup`
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "name": "Jane Doe",
  "email": "user@example.com",
  "password": "SecretPassword123",
  "otp": "123456",
  "phone": "1234567890",
  "address": "123 Main Street",
  "city": "New York",
  "postalcode": "10001",
  "country": "United States"
}
```

#### Response (`201 Created`):
```json
{
  "message": "User registered successfully.",
  "userid": "e33e6355-597a-45eb-8999-b5a300af1a3b",
  "email": "user@example.com",
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "user": {
    "id": "e33e6355-597a-45eb-8999-b5a300af1a3b",
    "name": "Jane Doe",
    "email": "user@example.com",
    "role": "Owner"
  }
}
```

---

### 3.4 User Login

Authenticates user credentials and returns a JWT access token.

- **URL**: `POST /auth/login`
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "email": "user@example.com",
  "password": "SecretPassword123"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "user": {
    "id": "e33e6355-597a-45eb-8999-b5a300af1a3b",
    "name": "Jane Doe",
    "email": "user@example.com",
    "role": "Owner"
  }
}
```

---

### 3.5 Reset Password (Unauthenticated / Forgot Password)

Resets user password using the 6-digit OTP sent to their email.

- **URL**: `POST /auth/reset-password`
- **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "email": "user@example.com",
  "otp": "654321",
  "new_password": "NewBrandPassword456"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Password reset successfully. You can now login with your new password."
}
```

---

### 3.6 Get Logged-in Profile

Fetches user profile details for an authenticated user.

- **URL**: `GET /auth/profile`
- **Headers**: `Authorization: Bearer <accessToken>`

#### Response (`200 OK`):
```json
{
  "userid": "e33e6355-597a-45eb-8999-b5a300af1a3b",
  "name": "Jane Doe",
  "email": "user@example.com",
  "phone": "1234567890",
  "address": "123 Main Street",
  "city": "New York",
  "postalcode": "10001",
  "country": "United States"
}
```

---

### 3.7 Profile Reset Password (Authenticated)

Resets user password from within user profile using a verified OTP.

- **URL**: `POST /auth/profile/reset-password`
- **Headers**:
  - `Authorization: Bearer <accessToken>`
  - `Content-Type: application/json`

#### Request Payload:
```json
{
  "email": "user@example.com",
  "otp": "654321",
  "new_password": "NewBrandPassword456"
}
```

#### Response (`200 OK`):
```json
{
  "success": true,
  "message": "Password reset successfully. You can now login with your new password."
}
```

---

## 4. JWT Token Payload Details

The `accessToken` returned on signup/login contains standard claims:

```json
{
  "sub": "e33e6355-597a-45eb-8999-b5a300af1a3b",
  "name": "Jane Doe",
  "email": "user@example.com",
  "phone": "1234567890",
  "role": "Owner",
  "exp": 1754023400
}
```

- `sub`: User ID (`UUID` string).
- `name`: User full name.
- `email`: Registered email.
- `phone`: Contact phone number.
- `role`: Role (`"Owner"`).
- `exp`: Unix timestamp indicating token expiry (60 mins).
