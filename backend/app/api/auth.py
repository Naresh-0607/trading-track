from fastapi import APIRouter

from app.core.dependencies import CurrentUser, Db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: Db): return await AuthService(UserRepository(db)).register(data)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Db): return await AuthService(UserRepository(db)).login(data)

@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser): return user

