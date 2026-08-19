from decimal import Decimal
from uuid import UUID

from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.services.errors import AppError


class AccountService:
    def __init__(self, repo: AccountRepository): self.repo = repo

    @staticmethod
    def present(item, pnl: object = 0, count: int = 0) -> AccountRead:
        value = Decimal(pnl or 0)
        return AccountRead.model_validate(item).model_copy(update={"account_pnl": value, "current_balance": item.initial_balance + value, "trade_count": count})

    async def list(self, user_id: UUID) -> list[AccountRead]:
        return [self.present(item, pnl, count) for item, pnl, count in await self.repo.list(user_id)]

    async def get(self, user_id: UUID, account_id: UUID) -> AccountRead:
        item = await self.repo.get(user_id, account_id)
        if not item: raise AppError(404, "Account not found")
        pnl, count = await self.repo.pnl_and_count(item.id); return self.present(item, pnl, count)

    async def create(self, user_id: UUID, data: AccountCreate) -> AccountRead:
        item = await self.repo.create(user_id, data.model_dump()); return self.present(item)

    async def update(self, user_id: UUID, account_id: UUID, data: AccountUpdate) -> AccountRead:
        item = await self.repo.get(user_id, account_id)
        if not item: raise AppError(404, "Account not found")
        item = await self.repo.update(item, data.model_dump(exclude_unset=True)); pnl, count = await self.repo.pnl_and_count(item.id)
        return self.present(item, pnl, count)

    async def delete(self, user_id: UUID, account_id: UUID) -> None:
        item = await self.repo.get(user_id, account_id)
        if not item: raise AppError(404, "Account not found")
        _, count = await self.repo.pnl_and_count(item.id)
        if count: raise AppError(400, "Cannot delete account with existing trades")
        await self.repo.delete(item)

