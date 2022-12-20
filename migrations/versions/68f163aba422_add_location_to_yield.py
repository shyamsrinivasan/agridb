"""add location to yield

Revision ID: 68f163aba422
Revises: ea3776fe7ca7
Create Date: 2022-12-20 23:48:26.641150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68f163aba422'
down_revision = 'ea3776fe7ca7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('yield', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', sa.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', name='field_location'), nullable=True))
        batch_op.create_index(batch_op.f('ix_yield_location'), ['location'], unique=False)
        batch_op.create_foreign_key(None, 'fields', ['location'], ['location'], onupdate='CASCADE', ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('yield', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_yield_location'))
        batch_op.drop_column('location')

    # ### end Alembic commands ###
