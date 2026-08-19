from datetime import UTC, datetime
from tests.conftest import register
from app.core.config import Settings


def test_neon_url_is_normalized_for_asyncpg():
    settings = Settings(database_url="postgresql://user:pass@host/db?sslmode=require&channel_binding=require")
    assert settings.database_url == "postgresql+asyncpg://user:pass@host/db?ssl=require"

async def test_register_login_and_invalid_login(client):
    response, headers = await register(client)
    assert response.status_code == 201 and response.json()["user"]["email"] == "trader@example.com"
    assert (await client.get("/api/v1/auth/me", headers=headers)).json()["name"] == "Trader"
    assert (await client.post("/api/v1/auth/login", json={"email":"trader@example.com","password":"strongpass123"})).status_code == 200
    assert (await client.post("/api/v1/auth/login", json={"email":"trader@example.com","password":"wrong"})).status_code == 401
    assert (await client.post("/api/v1/auth/register", json={"name":"Again","email":"TRADER@example.com","password":"strongpass123"})).status_code == 409
    assert (await client.post("/api/v1/auth/register", json={"name":"   ","email":"blank@example.com","password":"strongpass123"})).status_code == 422

async def test_account_ownership(client, auth):
    created = await client.post("/api/v1/accounts", headers=auth, json={"name":"Primary","broker":"IC Markets","account_type":"LIVE","initial_balance":"10000","currency":"USD"})
    assert created.status_code == 201 and created.json()["current_balance"] == "10000.00"
    _, other = await register(client, "other@example.com")
    assert (await client.get(f"/api/v1/accounts/{created.json()['id']}", headers=other)).status_code == 404

async def test_trade_ownership_listing_and_stats(client, auth):
    account = (await client.post("/api/v1/accounts", headers=auth, json={"name":"Prop","account_type":"PROP","initial_balance":"5000"})).json()
    _, other = await register(client, "other@example.com")
    bad = await client.post("/api/v1/trades", headers=other, json={"account_id":account["id"],"trade_date":datetime.now(UTC).isoformat(),"symbol":"EURUSD","side":"BUY","volume":"1","open_price":"1.1"})
    assert bad.status_code == 404
    trade_ids = []
    for symbol, side, pnl in [("EURUSD","BUY","200"),("GBPUSD","SELL","-50")]:
        response = await client.post("/api/v1/trades", headers=auth, json={"account_id":account["id"],"trade_date":datetime.now(UTC).isoformat(),"symbol":symbol,"asset_type":"FOREX","side":side,"volume":"1","open_price":"1.1","close_price":"1.2","pnl":pnl})
        assert response.status_code == 201
        trade_ids.append(response.json()["id"])
    listing = await client.get("/api/v1/trades?side=BUY", headers=auth)
    assert listing.json()["total"] == 1 and listing.json()["items"][0]["symbol"] == "EURUSD"
    stats = (await client.get("/api/v1/stats/overview?range=all", headers=auth)).json()
    assert stats["net_pnl"] == "150.00" and stats["win_rate"] == 50 and stats["profit_factor"] == 4
    account_after = (await client.get(f"/api/v1/accounts/{account['id']}", headers=auth)).json()
    assert account_after["current_balance"] == "5150.00"
    assert (await client.delete(f"/api/v1/accounts/{account['id']}", headers=auth)).status_code == 400
    updated = await client.patch(f"/api/v1/trades/{trade_ids[0]}", headers=auth, json={"comments":"Followed the plan"})
    assert updated.status_code == 200 and updated.json()["comments"] == "Followed the plan"
    assert (await client.delete(f"/api/v1/trades/{trade_ids[1]}", headers=auth)).status_code == 204
    assert (await client.get("/api/v1/trades", headers=auth)).json()["total"] == 1
