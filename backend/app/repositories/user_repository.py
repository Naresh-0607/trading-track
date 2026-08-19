from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession): self.db = db

    async def by_email(self, email: str) -> User | None:
        return await self.db.scalar(select(User).where(User.email == email))

    async def by_id(self, user_id: UUID) -> User | None:
        return await self.db.get(User, user_id)

    async def create(self, **values: object) -> User:
        user = User(**values)
        self.db.add(user)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(user)
        return user
