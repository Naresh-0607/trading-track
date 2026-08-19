from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.infrastructure.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.errors import AppError

bearer = HTTPBearer(auto_error=False)
Db = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user_id(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> UUID:
    if not credentials: raise AppError(401, "Authentication required")
    try: user_id = decode_access_token(credentials.credentials)
    except ValueError: raise AppError(401, "Invalid or expired token")
    return user_id


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]


async def get_current_user(db: Db, user_id: CurrentUserId) -> User:
    user = await UserRepository(db).by_id(user_id)
    if not user: raise AppError(401, "Authentication required")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
