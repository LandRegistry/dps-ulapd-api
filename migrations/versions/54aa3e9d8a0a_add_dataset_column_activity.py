"""empty message

Revision ID: 54aa3e9d8a0a
Revises: c17fa890e151
Create Date: 2019-11-18 15:38:10.639096

"""
from alembic import op
from sqlalchemy import Column, String


# revision identifiers, used by Alembic.
revision = '54aa3e9d8a0a'
down_revision = 'c17fa890e151'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('activity', Column('dataset_id', String()))


def downgrade():
    op.drop_column('activity', 'dataset_id')
