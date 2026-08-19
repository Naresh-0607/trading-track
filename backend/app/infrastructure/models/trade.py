import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums.trade_side import AssetType, TradeSide
from app.domain.enums.trade_source import TradeSource
from app.infrastructure.models.base import UUIDTimestampMixin


class Trade(UUIDTimestampMixin, Base):
    __tablename__ = "trades"
    __table_args__ = (Index("ix_trades_external_trade_id", "external_trade_id"),)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), index=True)
    trade_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    symbol: Mapped[str] = mapped_column(String(32))
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType, name="asset_type"))
    side: Mapped[TradeSide] = mapped_column(Enum(TradeSide, name="trade_side"))
    volume: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    open_price: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    close_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 8), nullable=True)
    stop_loss: Mapped[Decimal | None] = mapped_column(Numeric(24, 8), nullable=True)
    take_profit: Mapped[Decimal | None] = mapped_column(Numeric(24, 8), nullable=True)
    pnl: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[TradeSource] = mapped_column(Enum(TradeSource, name="trade_source"), default=TradeSource.MANUAL)
    external_trade_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    external_account_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sync_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    user: Mapped["User"] = relationship(back_populates="trades")  # noqa: F821
    account: Mapped["Account"] = relationship(back_populates="trades")  # noqa: F821

