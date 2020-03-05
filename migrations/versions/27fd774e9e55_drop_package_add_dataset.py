"""empty message

Revision ID: 27fd774e9e55
Revises: 54aa3e9d8a0a
Create Date: 2019-11-18 16:44:21.709777

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from flask import current_app

# revision identifiers, used by Alembic.
revision = '27fd774e9e55'
down_revision = '54aa3e9d8a0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dataset',
    sa.Column('dataset_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('version', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('licence_id', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('private', sa.Boolean(), nullable=True),
    sa.Column('external', sa.Boolean(), nullable=True),
    sa.Column('metadata_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('dataset_id'),
    sa.UniqueConstraint('name')
    )
    op.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE dataset TO " + current_app.config.get('APP_SQL_USERNAME'))
    op.execute("GRANT USAGE, SELECT ON dataset_dataset_id_seq TO " + current_app.config.get('APP_SQL_USERNAME'))

    op.drop_table('package')
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('dataset')
    op.create_table('package',
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('licence_id', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('private', sa.Boolean(), nullable=True),
        sa.Column('external', sa.Boolean(), nullable=True),
        sa.Column('metadata_created', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('package_id'),
        sa.UniqueConstraint('name')
    )
    op.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE package TO " + current_app.config.get('APP_SQL_USERNAME'))
    op.execute("GRANT USAGE, SELECT ON package_package_id_seq TO " + current_app.config.get('APP_SQL_USERNAME'))

    # ### end Alembic commands ###