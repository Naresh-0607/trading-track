"""initial schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"; down_revision = None; branch_labels = None; depends_on = None

def upgrade():
    account_type = sa.Enum("LIVE", "DEMO", "PROP", "OTHER", name="account_type")
    asset_type = sa.Enum("FOREX", "STOCK", "CRYPTO", "COMMODITY", "INDEX", "OTHER", name="asset_type")
    trade_side = sa.Enum("BUY", "SELL", name="trade_side")
    trade_source = sa.Enum("MANUAL", "EXTERNAL", name="trade_source")
    op.create_table("users", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(320), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("accounts", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False), sa.Column("broker", sa.String(120), nullable=False), sa.Column("account_type", account_type, nullable=False),
        sa.Column("initial_balance", sa.Numeric(18,2), nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])
    op.create_table("trades", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False), sa.Column("trade_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=False), sa.Column("asset_type", asset_type, nullable=False), sa.Column("side", trade_side, nullable=False),
        sa.Column("volume", sa.Numeric(18,6), nullable=False), sa.Column("open_price", sa.Numeric(24,8), nullable=False), sa.Column("close_price", sa.Numeric(24,8)),
        sa.Column("stop_loss", sa.Numeric(24,8)), sa.Column("take_profit", sa.Numeric(24,8)), sa.Column("pnl", sa.Numeric(18,2)), sa.Column("comments", sa.Text()),
        sa.Column("source", trade_source, nullable=False), sa.Column("external_trade_id", sa.String(128)), sa.Column("external_account_id", sa.String(128)), sa.Column("sync_status", sa.String(32)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    for column in ("user_id", "account_id", "trade_date", "external_trade_id"): op.create_index(f"ix_trades_{column}", "trades", [column])

def downgrade():
    op.drop_table("trades"); op.drop_table("accounts"); op.drop_table("users")
    for name in ("trade_source", "trade_side", "asset_type", "account_type"): sa.Enum(name=name).drop(op.get_bind())

