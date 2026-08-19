from uuid import UUID
from fastapi import APIRouter, Response
from app.core.dependencies import CurrentUserId, Db
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])
def service(db): return AccountService(AccountRepository(db))

@router.get("", response_model=list[AccountRead])
async def list_accounts(user_id: CurrentUserId, db: Db): return await service(db).list(user_id)
@router.post("", response_model=AccountRead, status_code=201)
async def create_account(data: AccountCreate, user_id: CurrentUserId, db: Db): return await service(db).create(user_id, data)
@router.get("/{account_id}", response_model=AccountRead)
async def get_account(account_id: UUID, user_id: CurrentUserId, db: Db): return await service(db).get(user_id, account_id)
@router.patch("/{account_id}", response_model=AccountRead)
async def update_account(account_id: UUID, data: AccountUpdate, user_id: CurrentUserId, db: Db): return await service(db).update(user_id, account_id, data)
@router.delete("/{account_id}", status_code=204)
async def delete_account(account_id: UUID, user_id: CurrentUserId, db: Db): await service(db).delete(user_id, account_id); return Response(status_code=204)
