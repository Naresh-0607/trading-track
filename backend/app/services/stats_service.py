from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from app.repositories.account_repository import AccountRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.stats import AccountPerformance, PnlPoint, StatsOverview


class StatsService:
    def __init__(self, trades: TradeRepository, accounts: AccountRepository): self.trades = trades; self.accounts = accounts

    async def overview(self, user_id: UUID, range_: str) -> StatsOverview:
        days = {"7d": 7, "1m": 30, "3m": 90}.get(range_)
        since = datetime.now(UTC) - timedelta(days=days) if days else None
        trades = await self.trades.for_stats(user_id, since)
        closed = [t for t in trades if t.pnl is not None]
        wins = [t.pnl for t in closed if t.pnl > 0]; losses = [t.pnl for t in closed if t.pnl < 0]
        gross_profit = sum(wins, Decimal(0)); gross_loss = sum(losses, Decimal(0)); net = gross_profit + gross_loss
        cumulative = Decimal(0); history = []
        for trade in closed:
            cumulative += trade.pnl
            history.append(PnlPoint(date=trade.trade_date.date().isoformat(), pnl=trade.pnl, cumulative_pnl=cumulative))
        accounts = await self.accounts.list(user_id)
        names = {account.id: account.name for account, _, _ in accounts}
        totals: dict[UUID, Decimal] = {}
        for trade in closed:
            totals[trade.account_id] = totals.get(trade.account_id, Decimal(0)) + trade.pnl
        performance = [AccountPerformance(account_id=account_id, name=names.get(account_id, "Account"), pnl=pnl) for account_id, pnl in totals.items()]
        return StatsOverview(net_pnl=net, win_rate=round(len(wins)/len(closed)*100, 2) if closed else 0,
            profit_factor=round(float(gross_profit / abs(gross_loss)), 2) if gross_loss else (None if gross_profit else 0),
            average_win=gross_profit/len(wins) if wins else 0, average_loss=gross_loss/len(losses) if losses else 0,
            total_trades=len(closed), buy_count=sum(t.side.value == "BUY" for t in closed), sell_count=sum(t.side.value == "SELL" for t in closed),
            pnl_history=history, account_performance=performance)
