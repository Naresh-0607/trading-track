from __future__ import annotations

import math
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums.trade_side import AssetType, TradeSide
from app.infrastructure.models.trade import Trade


class TradeRepository:
    def __init__(self, db: AsyncSession): self.db = db

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
