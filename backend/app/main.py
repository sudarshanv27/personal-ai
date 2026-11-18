from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.database.connection import engine


app = FastAPI(
    title="Personal AI",
    description="Private Personal AI Assistant",
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTER
# ============================================================

app.include_router(
    api_router,
    prefix="/api",
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "Personal AI",
        "status": "online",
        "version": "0.1.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }