from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.account import Account
from app.infrastructure.models.trade import Trade


class AccountRepository:
    def __init__(self, db: AsyncSession): self.db = db

    async def list(self, user_id: UUID) -> list[tuple[Account, object, int]]:
        stmt = (select(Account, func.coalesce(func.sum(Trade.pnl), 0), func.count(Trade.id))
                .outerjoin(Trade, Trade.account_id == Account.id).where(Account.user_id == user_id)
                .group_by(Account.id).order_by(Account.created_at.desc()))
        return list((await self.db.execute(stmt)).all())

    async def get(self, user_id: UUID, account_id: UUID) -> Account | None:
        return await self.db.scalar(select(Account).where(Account.id == account_id, Account.user_id == user_id))

    async def pnl_and_count(self, account_id: UUID) -> tuple[object, int]:
        row = (await self.db.execute(select(func.coalesce(func.sum(Trade.pnl), 0), func.count(Trade.id)).where(Trade.account_id == account_id))).one()
        return row[0], row[1]

    async def create(self, user_id: UUID, values: dict) -> Account:
        item = Account(user_id=user_id, **values); self.db.add(item); await self.db.commit(); await self.db.refresh(item); return item

    async def update(self, item: Account, values: dict) -> Account:
        for key, value in values.items(): setattr(item, key, value)
        await self.db.commit(); await self.db.refresh(item); return item

    async def delete(self, item: Account) -> None:
        await self.db.delete(item); await self.db.commit()

