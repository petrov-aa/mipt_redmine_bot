"""long url

Revision ID: 1ea6ddf58753
Revises: 38e8b2265067
Create Date: 2018-04-25 22:03:39.440353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ea6ddf58753'
down_revision = '38e8b2265067'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feed', sa.Column('url', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feed', 'url')
    # ### end Alembic commands ###
