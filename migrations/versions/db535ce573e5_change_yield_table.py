"""change yield table

Revision ID: db535ce573e5
Revises: 68f163aba422
Create Date: 2022-12-22 16:51:00.578907

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'db535ce573e5'
down_revision = '68f163aba422'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('yield_entry')
    with op.batch_alter_table('yield', schema=None) as batch_op:
        batch_op.drop_constraint('yield_ibfk_1', type_='foreignkey')
        batch_op.drop_index('ix_yield_sowing_id')
        batch_op.drop_column('sowing_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('yield', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sowing_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('yield_ibfk_1', 'sowing', ['sowing_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.create_index('ix_yield_sowing_id', ['sowing_id'], unique=False)

    op.create_table('yield_entry',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('yield_entry_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('harvest_date', sa.DATE(), nullable=True),
    sa.Column('sell_date', sa.DATE(), nullable=True),
    sa.Column('bags', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('bag_weight', mysql.FLOAT(), nullable=True),
    sa.Column('bag_rate', mysql.FLOAT(), nullable=True),
    sa.Column('buyer', mysql.VARCHAR(length=15), nullable=True),
    sa.ForeignKeyConstraint(['yield_entry_id'], ['yield.id'], name='yield_entry_ibfk_1', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###