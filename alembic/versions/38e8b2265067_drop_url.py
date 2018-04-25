"""drop url

Revision ID: 38e8b2265067
Revises: 2ab7dc665c15
Create Date: 2018-04-25 22:03:06.203949

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '38e8b2265067'
down_revision = '2ab7dc665c15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feed', 'url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feed', sa.Column('url', mysql.VARCHAR(collation='utf8_unicode_ci', length=255), nullable=True))
    # ### end Alembic commands ###
