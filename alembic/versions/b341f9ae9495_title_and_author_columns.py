"""title and author columns

Revision ID: b341f9ae9495
Revises: a672063cafeb
Create Date: 2018-04-26 03:31:14.433467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b341f9ae9495'
down_revision = 'a672063cafeb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feed', sa.Column('author', sa.String(length=255), nullable=True))
    op.add_column('feed', sa.Column('title', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feed', 'title')
    op.drop_column('feed', 'author')
    # ### end Alembic commands ###
