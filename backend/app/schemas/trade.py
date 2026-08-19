from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums.trade_side import AssetType, TradeSide
from app.domain.enums.trade_source import TradeSource


class TradeCreate(BaseModel):
    account_id: UUID
    trade_date: datetime
    symbol: str = Field(min_length=1, max_length=32)
    asset_type: AssetType = AssetType.OTHER
    side: TradeSide
    volume: Decimal = Field(gt=0)
    open_price: Decimal = Field(gt=0)
    close_price: Decimal | None = Field(default=None, gt=0)
    stop_loss: Decimal | None = Field(default=None, gt=0)
    take_profit: Decimal | None = Field(default=None, gt=0)
    comments: str | None = Field(default=None, max_length=5000)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("Symbol must not be empty")
        return value


class TradeUpdate(BaseModel):
    account_id: UUID | None = None
    trade_date: datetime | None = None
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    asset_type: AssetType | None = None
    side: TradeSide | None = None
    volume: Decimal | None = Field(default=None, gt=0)
    open_price: Decimal | None = Field(default=None, gt=0)
    close_price: Decimal | None = Field(default=None, gt=0)
    stop_loss: Decimal | None = Field(default=None, gt=0)
    take_profit: Decimal | None = Field(default=None, gt=0)
    comments: str | None = Field(default=None, max_length=5000)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().upper()
        if not value:
            raise ValueError("Symbol must not be empty")
        return value


class TradeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    account_id: UUID
    trade_date: datetime
    symbol: str
    asset_type: AssetType
    side: TradeSide
    volume: Decimal
    open_price: Decimal
    close_price: Decimal | None
    stop_loss: Decimal | None
    take_profit: Decimal | None
    pnl: Decimal | None
    comments: str | None
    source: TradeSource
    external_trade_id: str | None
    external_account_id: str | None
    sync_status: str | None
    created_at: datetime
    updated_at: datetime


class TradePage(BaseModel):
    items: list[TradeRead]
    total: int
    page: int
    page_size: int
    pages: int
