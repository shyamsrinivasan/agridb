"""add location FK to equipments

Revision ID: 9010831cf655
Revises: ceeca6cdafaf
Create Date: 2022-12-23 23:51:06.580540

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9010831cf655'
down_revision = 'ceeca6cdafaf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('equipments', schema=None) as batch_op:
        batch_op.alter_column('location',
               existing_type=mysql.ENUM('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'none'),
               nullable=True)
        batch_op.drop_index('ix_equipments_location')
        batch_op.create_foreign_key(None, 'fields', ['location'], ['location'], onupdate='CASCADE', ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('equipments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_index('ix_equipments_location', ['location'], unique=False)
        batch_op.alter_column('location',
               existing_type=mysql.ENUM('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'none'),
               nullable=False)

    # ### end Alembic commands ###
