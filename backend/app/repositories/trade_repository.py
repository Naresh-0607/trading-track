from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums.trade_side import AssetType, TradeSide
from app.infrastructure.models.trade import Trade


class TradeRepository:
    def __init__(self, db: AsyncSession): self.db = db

    @staticmethod
    def _closed_pnl():
        return case(
            (
                and_(Trade.close_price.is_not(None), Trade.pnl.is_not(None)),
                Trade.pnl,
            ),
            else_=Decimal("0.00"),
        )

    async def list(self, user_id: UUID, *, account_id: UUID | None, side: TradeSide | None, symbol: str | None,
                   asset_type: AssetType | None, search: str | None, page: int, page_size: int) -> tuple[list[Trade], int]:
        filters = [Trade.user_id == user_id]
        if account_id: filters.append(Trade.account_id == account_id)
        if side: filters.append(Trade.side == side)
        if symbol: filters.append(Trade.symbol.ilike(f"%{symbol}%"))
        if asset_type: filters.append(Trade.asset_type == asset_type)
        if search: filters.append(or_(Trade.symbol.ilike(f"%{search}%"), Trade.comments.ilike(f"%{search}%")))
        statement = (select(Trade, func.count().over().label("total_count"))
                     .where(*filters).order_by(Trade.trade_date.desc())
                     .offset((page - 1) * page_size).limit(page_size))
        rows = list((await self.db.execute(statement)).all())
        items = [row[0] for row in rows]
        total = rows[0][1] if rows else 0
        if not rows and page > 1:
            total = await self.db.scalar(select(func.count()).select_from(Trade).where(*filters)) or 0
        return items, total

    async def get(self, user_id: UUID, trade_id: UUID) -> Trade | None:
        return await self.db.scalar(select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id))

    async def create(self, user_id: UUID, values: dict) -> Trade:
        item = Trade(user_id=user_id, **values); self.db.add(item); await self.db.commit(); await self.db.refresh(item); return item

    async def update(self, item: Trade, values: dict) -> Trade:
        for key, value in values.items(): setattr(item, key, value)
        await self.db.commit(); await self.db.refresh(item); return item

    async def delete(self, item: Trade) -> None:
        await self.db.delete(item); await self.db.commit()

    async def for_stats(self, user_id: UUID, since: datetime | None) -> list[Trade]:
        filters = [Trade.user_id == user_id]
        if since: filters.append(Trade.trade_date >= since)
        return list((await self.db.scalars(select(Trade).where(*filters).order_by(Trade.trade_date))).all())

    async def calendar_month(self, user_id: UUID, start: datetime, end: datetime) -> list[tuple[object, object, int]]:
        trade_day = func.date(Trade.trade_date)
        statement = (
            select(
                trade_day.label("trade_day"),
                func.coalesce(func.sum(self._closed_pnl()), Decimal("0.00")).label("pnl"),
                func.count(Trade.id).label("trade_count"),
            )
            .where(Trade.user_id == user_id, Trade.trade_date >= start, Trade.trade_date < end)
            .group_by(trade_day)
            .order_by(trade_day)
        )
        return [(row.trade_day, row.pnl, row.trade_count) for row in (await self.db.execute(statement)).all()]

    async def calendar_day(self, user_id: UUID, start: datetime, end: datetime) -> tuple[object, int, list[Trade]]:
        filters = [Trade.user_id == user_id, Trade.trade_date >= start, Trade.trade_date < end]
        totals = (
            await self.db.execute(
                select(
                    func.coalesce(func.sum(self._closed_pnl()), Decimal("0.00")),
                    func.count(Trade.id),
                ).where(*filters)
            )
        ).one()
        trades = list((await self.db.scalars(select(Trade).where(*filters).order_by(Trade.trade_date))).all())
        return totals[0], totals[1], trades
