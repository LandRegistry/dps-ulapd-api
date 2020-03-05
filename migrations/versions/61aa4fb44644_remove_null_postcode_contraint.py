"""empty message

Revision ID: 61aa4fb44644
Revises: 27fd774e9e55
Create Date: 2019-12-04 14:38:12.826940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61aa4fb44644'
down_revision = '27fd774e9e55'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user_details', 'postcode', nullable=True)


def downgrade():
    op.alter_column('user_details', 'postcode', nullable=False)
