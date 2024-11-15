"""adding iban to userstable

Revision ID: 5a2cf193ca46
Revises: ed8fcc5a2bf8
Create Date: 2024-10-20 16:01:17.340816

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5a2cf193ca46'
down_revision = 'ed8fcc5a2bf8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('iban', sa.String(length=255), server_default='BG80BNBG96611020345678', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('iban')

    # ### end Alembic commands ###
