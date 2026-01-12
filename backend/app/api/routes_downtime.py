from fastapi import APIRouter
from app.services.downtime_service import get_downtime_summary

router = APIRouter(prefix="/downtime", tags=["Downtime"])


@router.get("/daily")
def daily_downtime(line_code: str, date: str):
    return get_downtime_summary(line_code, date)
