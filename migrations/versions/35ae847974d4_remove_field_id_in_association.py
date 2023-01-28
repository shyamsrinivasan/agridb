"""remove field_id in Association

Revision ID: 35ae847974d4
Revises: 3dbae032df4e
Create Date: 2023-01-28 15:48:44.838577

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '35ae847974d4'
down_revision = '3dbae032df4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fieldlink', schema=None) as batch_op:
        batch_op.drop_constraint('fieldlink_ibfk_1', type_='foreignkey')
        batch_op.drop_column('field_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fieldlink', schema=None) as batch_op:
        batch_op.add_column(sa.Column('field_id', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('fieldlink_ibfk_1', 'fields', ['field_id'], ['id'])

    # ### end Alembic commands ###
