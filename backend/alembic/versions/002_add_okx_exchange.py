"""Add OKX exchange

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE exchange ADD VALUE IF NOT EXISTS 'OKX'")


def downgrade() -> None:
    op.execute("""
        ALTER TYPE exchange RENAME TO exchange_old;
        CREATE TYPE exchange AS ENUM ('BINANCE', 'BYBIT');
        ALTER TABLE bots ALTER COLUMN exchange TYPE exchange USING exchange::text::exchange;
        DROP TYPE exchange_old;
    """)
