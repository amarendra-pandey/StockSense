"""add holding value constraints

Revision ID: d1c44630ea78
Revises: 08b651fba5ad
Create Date: 2026-10-22 07:35:54.635779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1c44630ea78'
down_revision: Union[str, Sequence[str], None] = '08b651fba5ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("holdings") as batch_op:
        batch_op.drop_index("ix_holdings_user_id")
        batch_op.create_check_constraint(
            "ck_holdings_quantity_positive",
            "quantity > 0",
        )
        batch_op.create_check_constraint(
            "ck_holdings_average_buy_price_positive",
            "average_buy_price > 0",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("holdings") as batch_op:
        batch_op.drop_constraint("ck_holdings_average_buy_price_positive", type_="check")
        batch_op.drop_constraint("ck_holdings_quantity_positive", type_="check")
        batch_op.create_index("ix_holdings_user_id", ["user_id"], unique=False)
