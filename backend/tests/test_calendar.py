from tests.conftest import register


async def create_account(client, headers, name="Primary"):
    response = await client.post(
        "/api/v1/accounts",
        headers=headers,
        json={"name": name, "account_type": "LIVE", "initial_balance": "10000"},
    )
    assert response.status_code == 201
    return response.json()


async def create_trade(client, headers, account_id, trade_date, pnl=None, close_price="101"):
    body = {
        "account_id": account_id,
        "trade_date": trade_date,
        "symbol": "AAPL",
        "asset_type": "STOCK",
        "side": "BUY",
        "volume": "1",
        "open_price": "100",
        "comments": "Calendar test trade",
    }
    if close_price is not None:
        body["close_price"] = close_price
    if pnl is not None:
        body["pnl"] = pnl
    response = await client.post("/api/v1/trades", headers=headers, json=body)
    assert response.status_code == 201
    return response.json()


async def test_calendar_month_aggregates_profit_loss_zero_and_counts_all_trades(client, auth):
    account = await create_account(client, auth)
    await create_trade(client, auth, account["id"], "2026-08-05T09:30:00Z", "120.50")
    await create_trade(client, auth, account["id"], "2026-08-05T11:00:00Z", close_price=None)
    await create_trade(client, auth, account["id"], "2026-08-06T09:30:00Z", "-25.25")
    await create_trade(client, auth, account["id"], "2026-08-07T09:30:00Z", "0")
    # A PnL on a trade without a close price is not a valid closed-trade result.
    await create_trade(client, auth, account["id"], "2026-08-08T09:30:00Z", "99", close_price=None)
    await create_trade(client, auth, account["id"], "2026-09-01T09:30:00Z", "500")

    response = await client.get("/api/v1/calendar?year=2026&month=8", headers=auth)

    assert response.status_code == 200
    assert response.json() == [
        {"date": "2026-08-05", "pnl": "120.50", "trade_count": 2},
        {"date": "2026-08-06", "pnl": "-25.25", "trade_count": 1},
        {"date": "2026-08-07", "pnl": "0.00", "trade_count": 1},
        {"date": "2026-08-08", "pnl": "0.00", "trade_count": 1},
    ]
    losing_day = (await client.get("/api/v1/calendar/2026-08-06", headers=auth)).json()
    zero_day = (await client.get("/api/v1/calendar/2026-08-07", headers=auth)).json()
    assert losing_day["status"] == "loss"
    assert zero_day["status"] == "neutral"


async def test_calendar_day_returns_summary_status_and_all_user_trades(client, auth):
    account = await create_account(client, auth)
    first = await create_trade(client, auth, account["id"], "2026-08-22T08:00:00Z", "75")
    second = await create_trade(client, auth, account["id"], "2026-08-22T14:00:00Z", "-20")
    await create_trade(client, auth, account["id"], "2026-08-23T08:00:00Z", "10")

    response = await client.get("/api/v1/calendar/2026-08-22", headers=auth)
    payload = response.json()

    assert response.status_code == 200
    assert payload["date"] == "2026-08-22"
    assert payload["pnl"] == "55.00"
    assert payload["status"] == "profit"
    assert payload["trade_count"] == 2
    assert [trade["id"] for trade in payload["trades"]] == [first["id"], second["id"]]
    assert payload["trades"][0]["comments"] == "Calendar test trade"


async def test_calendar_is_user_isolated(client, auth):
    account = await create_account(client, auth)
    await create_trade(client, auth, account["id"], "2026-08-22T08:00:00Z", "20")

    _, other_headers = await register(client, "calendar-other@example.com")
    other_account = await create_account(client, other_headers, "Other")
    await create_trade(client, other_headers, other_account["id"], "2026-08-22T09:00:00Z", "999")

    month = (await client.get("/api/v1/calendar?year=2026&month=8", headers=auth)).json()
    day = (await client.get("/api/v1/calendar/2026-08-22", headers=auth)).json()

    assert month == [{"date": "2026-08-22", "pnl": "20.00", "trade_count": 1}]
    assert day["pnl"] == "20.00"
    assert day["trade_count"] == 1
    assert all(trade["account_id"] == account["id"] for trade in day["trades"])


async def test_calendar_empty_date_is_neutral_and_endpoints_require_auth(client, auth):
    response = await client.get("/api/v1/calendar/2026-08-30", headers=auth)

    assert response.status_code == 200
    assert response.json() == {
        "date": "2026-08-30",
        "pnl": "0.00",
        "trade_count": 0,
        "status": "neutral",
        "trades": [],
    }
    assert (await client.get("/api/v1/calendar?year=2026&month=8")).status_code == 401
    assert (await client.get("/api/v1/calendar/2026-08-30")).status_code == 401
