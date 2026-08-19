from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PnlPoint(BaseModel):
    date: str
    pnl: Decimal
    cumulative_pnl: Decimal


class AccountPerformance(BaseModel):
    account_id: UUID
    name: str
    pnl: Decimal


class StatsOverview(BaseModel):
    net_pnl: Decimal
    win_rate: float
    profit_factor: float | None
    average_win: Decimal
    average_loss: Decimal
    total_trades: int
    buy_count: int
    sell_count: int
    pnl_history: list[PnlPoint]
    account_performance: list[AccountPerformance]

