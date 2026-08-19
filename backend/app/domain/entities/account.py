from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from app.domain.enums.account_type import AccountType


@dataclass(frozen=True, slots=True)
class AccountEntity:
    id: UUID
    user_id: UUID
    name: str
    broker: str
    account_type: AccountType
    initial_balance: Decimal
    currency: str
    is_active: bool

