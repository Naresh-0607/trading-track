from uuid import UUID

from app.domain.enums.trade_source import TradeSource
from app.integrations.base import BrokerAdapter
from app.schemas.trade import TradeCreate
from app.services.trade_service import TradeService


class SyncService:
    def __init__(self, adapter: BrokerAdapter, trades: TradeService): self.adapter = adapter; self.trades = trades

    async def sync_trades(self, user_id: UUID) -> int:
        imported = 0
        for payload in await self.adapter.get_trades():
            external = {k: payload.pop(k, None) for k in ("external_trade_id", "external_account_id", "sync_status")}
            await self.trades.create(user_id, TradeCreate.model_validate(payload), TradeSource.EXTERNAL, external); imported += 1
        return imported

