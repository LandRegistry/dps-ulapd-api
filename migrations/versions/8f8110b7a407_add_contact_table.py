"""add contact table

Revision ID: 8f8110b7a407
Revises: 61aa4fb44644
Create Date: 2019-12-06 12:57:48.887571

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app


# revision identifiers, used by Alembic.
revision = '8f8110b7a407'
down_revision = '61aa4fb44644'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('contact',
                    sa.Column('contact_id', sa.Integer(), nullable=False),
                    sa.Column('user_details_id', sa.Integer(), nullable=False),
                    sa.Column('contact_type', sa.String(), nullable=False),
                    sa.Column('date_added', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['user_details_id'], ['user_details.user_details_id'], ),
                    sa.PrimaryKeyConstraint('contact_id')
                    )
    op.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE contact TO " + current_app.config.get('APP_SQL_USERNAME'))
    op.execute("GRANT USAGE, SELECT ON contact_contact_id_seq TO " + current_app.config.get('APP_SQL_USERNAME'))

    op.alter_column('activity', 'dataset_id',
                    existing_type=sa.VARCHAR(),
                    nullable=False)


def downgrade():
    op.alter_column('activity', 'dataset_id',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.drop_table('contact')
