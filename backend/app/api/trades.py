from uuid import UUID
from fastapi import APIRouter, Query, Response
from app.core.dependencies import CurrentUserId, Db
from app.domain.enums.trade_side import AssetType, TradeSide
from app.repositories.account_repository import AccountRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.trade import TradeCreate, TradePage, TradeRead, TradeUpdate
from app.services.trade_service import TradeService

router = APIRouter(prefix="/trades", tags=["trades"])
def service(db): return TradeService(TradeRepository(db), AccountRepository(db))

@router.get("", response_model=TradePage)
async def list_trades(user_id: CurrentUserId, db: Db, account_id: UUID | None = None, side: TradeSide | None = None,
    symbol: str | None = None, asset_type: AssetType | None = None, search: str | None = None,
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return await service(db).list(user_id, account_id=account_id, side=side, symbol=symbol, asset_type=asset_type, search=search, page=page, page_size=page_size)
@router.post("", response_model=TradeRead, status_code=201)
async def create_trade(data: TradeCreate, user_id: CurrentUserId, db: Db): return await service(db).create(user_id, data)
@router.get("/{trade_id}", response_model=TradeRead)
async def get_trade(trade_id: UUID, user_id: CurrentUserId, db: Db): return await service(db).get(user_id, trade_id)
@router.patch("/{trade_id}", response_model=TradeRead)
async def update_trade(trade_id: UUID, data: TradeUpdate, user_id: CurrentUserId, db: Db): return await service(db).update(user_id, trade_id, data)
@router.delete("/{trade_id}", status_code=204)
async def delete_trade(trade_id: UUID, user_id: CurrentUserId, db: Db): await service(db).delete(user_id, trade_id); return Response(status_code=204)
