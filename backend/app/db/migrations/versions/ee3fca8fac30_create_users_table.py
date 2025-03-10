"""Create users table

Revision ID: ee3fca8fac30
Revises: 
Create Date: 2025-03-09 02:49:33.411334

Doc: https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script
"""
from alembic import op
import sqlalchemy as sa


revision = 'ee3fca8fac30'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('record_data', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_records'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('records')
    # ### end Alembic commands ###
