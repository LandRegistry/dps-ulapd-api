"""populate user_type look-up table

Revision ID: c17fa890e151
Revises: cca2451bb1b4
Create Date: 2019-11-15 10:57:10.864273

"""
from alembic import op
import datetime


# revision identifiers, used by Alembic.
revision = 'c17fa890e151'
down_revision = 'cca2451bb1b4'
branch_labels = None
depends_on = None


def upgrade():
    insert_sql = "INSERT into user_type (user_type, date_added) VALUES('{}', '{}')"
    user_types = [
        'personal-uk',
        'personal-overseas',
        'organisation-uk',
        'organisation-overseas'
    ]
    for rows in user_types:
        op.execute(insert_sql.format(rows, datetime.datetime.utcnow()))


def downgrade():
    pass
