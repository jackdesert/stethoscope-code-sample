"""index on timestamp

Revision ID: 824f0a76b4fd
Revises: 42a6f947500c
Create Date: 2018-11-08 07:57:21.062736

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '824f0a76b4fd'
down_revision = '42a6f947500c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('rssi_readings__badge_id', table_name='rssi_readings')
    op.create_index('rssi_readings__timestamp', 'rssi_readings', ['timestamp'], unique=False)


def downgrade():
    op.create_index('rssi_readings__badge_id', 'rssi_readings', ['badge_id'], unique=False)
    op.drop_index('rssi_readings__timestamp', table_name='rssi_readings')
