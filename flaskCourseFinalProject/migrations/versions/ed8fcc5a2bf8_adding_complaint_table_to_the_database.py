"""adding complaint table to the database

Revision ID: ed8fcc5a2bf8
Revises: 8c1906d660f7
Create Date: 2024-10-12 16:09:21.296239

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ed8fcc5a2bf8'
down_revision = '8c1906d660f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('complaints',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('photo_url', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('create_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='state'), nullable=False),
    sa.Column('complainer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['complainer_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('complaints')
    # ### end Alembic commands ###
