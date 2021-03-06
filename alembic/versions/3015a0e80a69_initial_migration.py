"""Initial Migration

Revision ID: 3015a0e80a69
Revises:
Create Date: 2018-11-03 12:00:19.374605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3015a0e80a69'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # RssiReading
    op.create_table('rssi_readings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('badge_id', sa.Text(), nullable=False),
    sa.Column('beacon_1_id', sa.Text(), nullable=True),
    sa.Column('beacon_2_id', sa.Text(), nullable=True),
    sa.Column('beacon_3_id', sa.Text(), nullable=True),
    sa.Column('beacon_4_id', sa.Text(), nullable=True),
    sa.Column('beacon_5_id', sa.Text(), nullable=True),
    sa.Column('beacon_1_strength', sa.Integer(), nullable=True),
    sa.Column('beacon_2_strength', sa.Integer(), nullable=True),
    sa.Column('beacon_3_strength', sa.Integer(), nullable=True),
    sa.Column('beacon_4_strength', sa.Integer(), nullable=True),
    sa.Column('beacon_5_strength', sa.Integer(), nullable=True),
    sa.Column('pi_id', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),

    sa.PrimaryKeyConstraint('id', name=op.f('pk_rssi_readings'))
    )
    op.create_index('rssi_readings__badge_id', 'rssi_readings', ['badge_id'], unique=False)


    # TrainingRun
    op.create_table('training_runs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Text(), nullable=True),
    sa.Column('badge_id', sa.Text(), nullable=False),
    sa.Column('start_timestamp', sa.DateTime(), nullable=True),
    sa.Column('end_timestamp', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_training_runs'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('training_runs')
    op.drop_index('rssi_readings__badge_id', table_name='rssi_readings')
    op.drop_table('rssi_readings')
    # ### end Alembic commands ###
