"""badge strength

Revision ID: d64778b9cef5
Revises: 824f0a76b4fd
Create Date: 2018-12-06 09:09:51.520332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd64778b9cef5'
down_revision = '824f0a76b4fd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('rssi_readings', sa.Column('badge_strength', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('rssi_readings', 'badge_strength')
