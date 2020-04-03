"""add count column for order

Revision ID: 20374d889a37
Revises: 53d9723ebcbd
Create Date: 2020-04-02 23:39:48.417225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20374d889a37'
down_revision = '53d9723ebcbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('count', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'count')
    # ### end Alembic commands ###