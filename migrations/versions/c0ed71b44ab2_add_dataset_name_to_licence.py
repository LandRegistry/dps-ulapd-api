"""Add dataset name to the licence table

Revision ID: c0ed71b44ab2
Revises: 27e487326ae8
Create Date: 2020-02-13 08:25:07.927013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0ed71b44ab2'
down_revision = '27e487326ae8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('licence', sa.Column('dataset_name', sa.String(), nullable=True))


def downgrade():
    op.drop_column('licence', 'dataset_name')
