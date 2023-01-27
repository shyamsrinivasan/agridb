"""add sowing_id

Revision ID: 3dbae032df4e
Revises: 57011d15eef4
Create Date: 2023-01-27 15:39:50.852737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dbae032df4e'
down_revision = '57011d15eef4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('yield', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sowing_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_yield_sowing_id'), ['sowing_id'], unique=False)
        batch_op.create_foreign_key('fkc_yield_sowing_id', 'sowing', ['sowing_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('yield', schema=None) as batch_op:
        batch_op.drop_constraint('fkc_yield_sowing_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_yield_sowing_id'))
        batch_op.drop_column('sowing_id')

    # ### end Alembic commands ###
