"""delete telegram_id

Revision ID: 03c79bbb548e
Revises: e17fb094c3a0
Create Date: 2025-02-16 23:52:25.672152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03c79bbb548e'
down_revision: Union[str, None] = 'e17fb094c3a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'telegram_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('telegram_id', sa.BIGINT(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
