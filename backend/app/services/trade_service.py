import math
from uuid import UUID

from app.domain.enums.trade_side import AssetType, TradeSide
from app.domain.enums.trade_source import TradeSource
from app.repositories.account_repository import AccountRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.trade import TradeCreate, TradePage, TradeRead, TradeUpdate
from app.services.errors import AppError


class TradeService:
    def __init__(self, trades: TradeRepository, accounts: AccountRepository): self.trades = trades; self.accounts = accounts

    async def _account(self, user_id: UUID, account_id: UUID):
        account = await self.accounts.get(user_id, account_id)
        if not account: raise AppError(404, "Account not found")
        return account

    async def list(self, user_id: UUID, **filters) -> TradePage:
        items, total = await self.trades.list(user_id, **filters)
        size = filters["page_size"]
        return TradePage(items=[TradeRead.model_validate(x) for x in items], total=total, page=filters["page"], page_size=size, pages=math.ceil(total/size) if total else 0)

    async def get(self, user_id: UUID, trade_id: UUID) -> TradeRead:
        item = await self.trades.get(user_id, trade_id)
        if not item: raise AppError(404, "Trade not found")
        return TradeRead.model_validate(item)

    async def create(self, user_id: UUID, data: TradeCreate, source: TradeSource = TradeSource.MANUAL, external: dict | None = None) -> TradeRead:
        await self._account(user_id, data.account_id)
        values = data.model_dump(); values["source"] = source; values.update(external or {})
        return TradeRead.model_validate(await self.trades.create(user_id, values))

    async def update(self, user_id: UUID, trade_id: UUID, data: TradeUpdate) -> TradeRead:
        item = await self.trades.get(user_id, trade_id)
        if not item: raise AppError(404, "Trade not found")
        values = data.model_dump(exclude_unset=True)
        if "account_id" in values: await self._account(user_id, values["account_id"])
        return TradeRead.model_validate(await self.trades.update(item, values))

    async def delete(self, user_id: UUID, trade_id: UUID) -> None:
        item = await self.trades.get(user_id, trade_id)
        if not item: raise AppError(404, "Trade not found")
        await self.trades.delete(item)
