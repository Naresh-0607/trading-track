from typing import Literal
from fastapi import APIRouter
from app.core.dependencies import CurrentUserId, Db
from app.repositories.account_repository import AccountRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.stats import StatsOverview
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])
@router.get("/overview", response_model=StatsOverview)
async def overview(user_id: CurrentUserId, db: Db, range: Literal["7d", "1m", "3m", "all"] = "all"):
    return await StatsService(TradeRepository(db), AccountRepository(db)).overview(user_id, range)
