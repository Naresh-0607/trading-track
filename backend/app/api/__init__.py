from fastapi import APIRouter
from app.api import accounts, auth, stats, trades

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(trades.router)
api_router.include_router(stats.router)

