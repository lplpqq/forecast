"""added data source field

Revision ID: 3b41d8314807
Revises: d544d439b854
Create Date: 2024-01-30 18:18:18.917475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b41d8314807'
down_revision: Union[str, None] = 'd544d439b854'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hitstorical_hourly_weather', sa.Column('data_source', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hitstorical_hourly_weather', 'data_source')
    # ### end Alembic commands ###
