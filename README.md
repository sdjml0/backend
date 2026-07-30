# 🛒 E-Commerce FastAPI Backend

A high-performance, asynchronous Python REST API for managing an E-Commerce dashboard, stores, analytics, inventory, and user authentication. Built with **FastAPI**, **asyncpg**, and **PostgreSQL**.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Environment Configuration](#-environment-configuration)
- [Quick Start Guide](#-quick-start-guide)
  - [1. Clone & Set Up Virtual Environment](#1-clone--set-up-virtual-environment)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Database Setup & Seeding](#3-database-setup--seeding)
  - [4. Running the API Server](#4-running-the-api-server)
- [🐳 Running with Docker](#-running-with-docker)
- [🧪 Testing & DB Verification](#-testing--db-verification)
- [📖 API Documentation & Endpoints](#-api-documentation--endpoints)

---

## ✨ Features

- **Asynchronous DB Operations**: Fast non-blocking queries using `asyncpg` and PostgreSQL (supports Neon DB).
- **JWT Authentication**: User signup, login, and bearer token verification (`passlib`, `python-jose`).
- **Dashboard Analytics**: Revenue time-series, marketplace share, top-selling products, and inventory low-stock alerts.
- **Fallback / Mock Support**: Automatically runs in fallback mock mode if database connection is unavailable.
- **Auto Swagger & ReDoc Docs**: Fully interactive API documentation provided out-of-the-box by FastAPI.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **Database**: PostgreSQL / [Neon DB](https://neon.tech/) via [asyncpg](https://github.com/MagicStack/asyncpg)
- **Data Validation & Settings**: Pydantic v2 & `pydantic-settings`
- **Security**: PyJWT / `python-jose`, `passlib[bcrypt]`

---

## 📂 Project Structure

```text
.
├── main.py              # Application entry point & FastAPI setup
├── run_seed.py          # Script to seed database tables from seed.sql
├── test_fetch.py        # Database connection & query test script
├── seed.sql             # SQL schema and seed data
├── requirements.txt     # Python project dependencies
├── Dockerfile           # Production Docker configuration
├── .env                 # Environment variables configuration
├── core/                # Core modules (DB connection, config, auth dependencies)
├── routers/             # API route handlers (Auth, Analytics v1, Dashboard)
├── schemas/             # Pydantic schemas for request/response validation
├── services/            # Business logic layer
└── repositories/       # Data access layer
```

---

## ⚙️ Prerequisites

- **Python 3.10+** (Python 3.11 recommended)
- **PostgreSQL Database** (Local instance or cloud-hosted service such as Neon DB)
- **pip** and `venv` module

---

## 🔑 Environment Configuration

Create a `.env` file in the project root directory (or modify the existing one):

```ini
DATABASE_URL=postgresql://user:password@hostname:5432/dbname?sslmode=require
SECRET_KEY=your_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
PORT=8000
```

---

## 🚀 Quick Start Guide

### 1. Set Up Virtual Environment

It is recommended to use a virtual environment to manage dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows (Command Prompt):
# venv\Scripts\activate.bat

# Activate on Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Setup & Seeding

Ensure your `DATABASE_URL` is set in `.env`, then run the database seed script to populate tables with sample data:

```bash
python run_seed.py
```

### 4. Running the API Server

You can run the server in two ways:

#### Option A: Direct Python Execution
```bash
python main.py
```

#### Option B: Using Uvicorn CLI (Recommended for Development)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Once running, access the API root endpoint at:
`http://localhost:8000/`

---

## 🐳 Running with Docker

You can containerize and run the application using Docker:

### 1. Build Docker Image
```bash
docker build -t ecom-backend .
```

### 2. Run Container
```bash
docker run -d \
  --name ecom-backend-container \
  -p 8000:8000 \
  --env-file .env \
  ecom-backend
```

---

## 🧪 Testing & DB Verification

Run the test script to verify database connectivity and inspect live table record counts:

```bash
python test_fetch.py
```

---

## 📖 API Documentation & Endpoints

FastAPI automatically generates interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Summary of Available Routes

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API status and metadata check | No |
| `POST` | `/auth/signup` | Register a new user account | No |
| `POST` | `/auth/login` | Login and obtain JWT access token | No |
| `GET` | `/auth/profile` | Get logged-in user profile details | Yes (Bearer Token) |
| `GET` | `/dashboard` | Aggregated dashboard overview metrics | Optional |
| `GET` | `/v1/dashboard/overview` | Detailed v1 dashboard payload | Optional |
| `GET` | `/v1/stores` | Connected marketplace stores | Optional |
| `GET` | `/v1/metrics/kpi` | Key Performance Indicator cards | Optional |
| `GET` | `/v1/analytics/revenue` | Revenue time-series analytics | Optional |
| `GET` | `/v1/analytics/marketplace-share` | Marketplace sales percentage breakdown | Optional |
| `GET` | `/v1/orders/recent` | Recent order list | Optional |
| `GET` | `/v1/products/top-selling` | Top selling product rankings | Optional |
| `GET` | `/v1/inventory/alerts` | Inventory low stock alerts | Optional |