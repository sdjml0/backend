from contextlib import asynccontextmanager
import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import db
from routers.auth_router import router as auth_router
from routers.dashboard_router import router as dashboard_router
from routers.api_v1_router import router as api_v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await db.connect()
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL connection failed ({e}). Running in API mock/fallback mode.")

    yield

    # Shutdown
    try:
        await db.disconnect()
    except Exception:
        pass


app = FastAPI(
    title="E-Commerce API",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {
        "message": "E-Commerce API is running.",
        "version": "1.0.0",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)