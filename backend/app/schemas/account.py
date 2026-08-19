from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums.account_type import AccountType


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    broker: str = Field(default="", max_length=120)
    account_type: AccountType = AccountType.OTHER
    initial_balance: Decimal = Decimal("0")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Account name must not be empty")
        return value

    @field_validator("broker")
    @classmethod
    def strip_broker(cls, value: str) -> str:
        return value.strip()

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    broker: str | None = Field(default=None, max_length=120)
    account_type: AccountType | None = None
    initial_balance: Decimal | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Account name must not be empty")
        return value

    @field_validator("broker")
    @classmethod
    def strip_broker(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else value


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    broker: str
    account_type: AccountType
    initial_balance: Decimal
    currency: str
    is_active: bool
    account_pnl: Decimal = Decimal("0")
    current_balance: Decimal = Decimal("0")
    trade_count: int = 0
    created_at: datetime
    updated_at: datetime
