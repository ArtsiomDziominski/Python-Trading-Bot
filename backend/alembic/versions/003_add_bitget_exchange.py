"""Add Bitget exchange

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE exchange ADD VALUE IF NOT EXISTS 'BITGET'")


def downgrade() -> None:
    op.execute("""
        ALTER TYPE exchange RENAME TO exchange_old;
        CREATE TYPE exchange AS ENUM ('BINANCE', 'BYBIT', 'OKX');
        ALTER TABLE bots ALTER COLUMN exchange TYPE exchange USING exchange::text::exchange;
        DROP TYPE exchange_old;
    """)
