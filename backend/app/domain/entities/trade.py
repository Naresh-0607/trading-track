from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.domain.enums.trade_side import AssetType, TradeSide
from app.domain.enums.trade_source import TradeSource


@dataclass(frozen=True, slots=True)
class TradeEntity:
    id: UUID
    user_id: UUID
    account_id: UUID
    trade_date: datetime
    symbol: str
    asset_type: AssetType
    side: TradeSide
    volume: Decimal
    open_price: Decimal
    pnl: Decimal | None
    source: TradeSource

