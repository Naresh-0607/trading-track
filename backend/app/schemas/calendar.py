from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.trade import TradeRead


class CalendarDaySummary(BaseModel):
    date: date
    pnl: Decimal
    trade_count: int


class CalendarDayDetail(CalendarDaySummary):
    status: Literal["profit", "loss", "neutral"]
    trades: list[TradeRead]
