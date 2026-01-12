# backend/app/api/routes_health.py

from fastapi import APIRouter
from sqlalchemy import text
from app.db.connection import engine

router = APIRouter()

@router.get("/health")
def health_check():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
