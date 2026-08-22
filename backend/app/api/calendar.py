from datetime import date

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUserId, Db
from app.repositories.trade_repository import TradeRepository
from app.schemas.calendar import CalendarDayDetail, CalendarDaySummary
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["calendar"])


def service(db):
    return CalendarService(TradeRepository(db))


@router.get("", response_model=list[CalendarDaySummary])
async def month(
    user_id: CurrentUserId,
    db: Db,
    year: int = Query(..., ge=1, le=9999),
    month: int = Query(..., ge=1, le=12),
):
    return await service(db).month(user_id, year, month)


@router.get("/{day}", response_model=CalendarDayDetail)
async def day(day: date, user_id: CurrentUserId, db: Db):
    return await service(db).day(user_id, day)
