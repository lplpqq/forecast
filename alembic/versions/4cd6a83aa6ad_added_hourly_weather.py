"""Added hourly_weather

Revision ID: 4cd6a83aa6ad
Revises: 8a7265a1b493
Create Date: 2024-01-28 01:08:17.807032

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4cd6a83aa6ad'
down_revision: Union[str, None] = '8a7265a1b493'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hourly_weather',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('pressure', sa.Float(), nullable=False),
    sa.Column('wind_speed', sa.Float(), nullable=False),
    sa.Column('wind_gust_speed', sa.Float(), nullable=False),
    sa.Column('wind_dir', sa.Float(), nullable=False),
    sa.Column('temperature', sa.Float(), nullable=False),
    sa.Column('feelslike_temp', sa.Float(), nullable=False),
    sa.Column('humidity', sa.Float(), nullable=False),
    sa.Column('clouds', sa.Float(), nullable=False),
    sa.Column('visibility', sa.Float(), nullable=False),
    sa.Column('precipitation', sa.Float(), nullable=False),
    sa.Column('snow', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hourly_weather')
    # ### end Alembic commands ###
