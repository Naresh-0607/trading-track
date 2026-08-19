from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.errors import AppError


class AuthService:
    def __init__(self, users: UserRepository): self.users = users

    async def register(self, data: RegisterRequest) -> TokenResponse:
        email = data.email.lower().strip()
        if await self.users.by_email(email): raise AppError(409, "Email already registered")
        try:
            user = await self.users.create(name=data.name.strip(), email=email, password_hash=hash_password(data.password))
        except IntegrityError:
            raise AppError(409, "Email already registered")
        return TokenResponse(access_token=create_access_token(user.id), user=UserRead.model_validate(user))

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.users.by_email(data.email.lower().strip())
        if not user or not verify_password(data.password, user.password_hash): raise AppError(401, "Invalid email or password")
        return TokenResponse(access_token=create_access_token(user.id), user=UserRead.model_validate(user))
from sqlalchemy.exc import IntegrityError

