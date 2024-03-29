"""drop category from models table

Revision ID: d8914cfa84bd
Revises: 28b8f1e29116
Create Date: 2022-12-20 09:40:36.579734

"""
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8914cfa84bd'
down_revision = '28b8f1e29116'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('model', 'category')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('model', sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
