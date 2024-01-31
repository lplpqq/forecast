"""tweaked the models

Revision ID: bd4393bf0594
Revises: 3b41d8314807
Create Date: 2024-01-31 16:08:32.578830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd4393bf0594'
down_revision: Union[str, None] = '3b41d8314807'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hitstorical_hourly_weather', sa.Column('apparent_temperature', sa.Float(), nullable=True))
    op.add_column('hitstorical_hourly_weather', sa.Column('wind_direction', sa.Float(), nullable=False))
    op.alter_column('hitstorical_hourly_weather', 'clouds',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.drop_column('hitstorical_hourly_weather', 'feelslike_temp')
    op.drop_column('hitstorical_hourly_weather', 'visibility')
    op.drop_column('hitstorical_hourly_weather', 'wind_dir')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hitstorical_hourly_weather', sa.Column('wind_dir', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.add_column('hitstorical_hourly_weather', sa.Column('visibility', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.add_column('hitstorical_hourly_weather', sa.Column('feelslike_temp', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.alter_column('hitstorical_hourly_weather', 'clouds',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.drop_column('hitstorical_hourly_weather', 'wind_direction')
    op.drop_column('hitstorical_hourly_weather', 'apparent_temperature')
    # ### end Alembic commands ###
