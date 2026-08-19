from abc import ABC, abstractmethod
from typing import Any


class BrokerAdapter(ABC):
    @abstractmethod
    async def get_accounts(self) -> list[dict[str, Any]]: ...
    @abstractmethod
    async def get_trades(self) -> list[dict[str, Any]]: ...
    @abstractmethod
    async def get_open_positions(self) -> list[dict[str, Any]]: ...

