from fastapi import APIRouter
from app.services.production_service import get_daily_production_summary

router = APIRouter(prefix="/production", tags=["Production"])


@router.get("/daily")
def daily_production(line_code: str, date: str):
    return get_daily_production_summary(line_code, date)
