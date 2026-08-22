from calendar import monthrange
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from app.repositories.trade_repository import TradeRepository
from app.schemas.calendar import CalendarDayDetail, CalendarDaySummary
from app.schemas.trade import TradeRead


class CalendarService:
    def __init__(self, trades: TradeRepository):
        self.trades = trades

    @staticmethod
    def _bounds(day: date) -> tuple[datetime, datetime]:
        start = datetime.combine(day, time.min, tzinfo=UTC)
        return start, start + timedelta(days=1)

    @staticmethod
    def _date(value: object) -> date:
        return value if isinstance(value, date) else date.fromisoformat(str(value))

    @staticmethod
    def _money(value: object) -> Decimal:
        return Decimal(str(value or "0")).quantize(Decimal("0.01"))

    async def month(self, user_id: UUID, year: int, month: int) -> list[CalendarDaySummary]:
        first = date(year, month, 1)
        last = date(year, month, monthrange(year, month)[1])
        start, _ = self._bounds(first)
        _, end = self._bounds(last)
        rows = await self.trades.calendar_month(user_id, start, end)
        return [
            CalendarDaySummary(date=self._date(day), pnl=self._money(pnl), trade_count=count)
            for day, pnl, count in rows
        ]

    async def day(self, user_id: UUID, day: date) -> CalendarDayDetail:
        start, end = self._bounds(day)
        pnl_value, count, trades = await self.trades.calendar_day(user_id, start, end)
        pnl = self._money(pnl_value)
        status = "profit" if pnl > 0 else "loss" if pnl < 0 else "neutral"
        return CalendarDayDetail(
            date=day,
            pnl=pnl,
            trade_count=count,
            status=status,
            trades=[TradeRead.model_validate(trade) for trade in trades],
        )
