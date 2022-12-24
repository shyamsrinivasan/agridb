"""remove field FK in land

Revision ID: df5c3ea25761
Revises: 9010831cf655
Create Date: 2022-12-24 12:39:35.636882

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'df5c3ea25761'
down_revision = '9010831cf655'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('account')
    op.drop_table('equipments')

    with op.batch_alter_table('lands', schema=None) as batch_op:
        batch_op.drop_constraint('lands_ibfk_1', type_='foreignkey')
        batch_op.drop_column('field_location')

    with op.batch_alter_table('fields', schema=None) as batch_op:
        batch_op.alter_column('location',
               existing_type=mysql.ENUM('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'house-yard', 'trichy-home1', 'trichy-home2'),
               type_=sa.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'trichy-home1', 'trichy-home2', 'house-yard', name='field_location'),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lands', schema=None) as batch_op:
        batch_op.add_column(sa.Column('field_location', mysql.ENUM('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'trichy-home1', 'trichy-home2', 'house-yard'), nullable=True))
        batch_op.create_foreign_key('lands_ibfk_1', 'fields', ['field_location'], ['location'], onupdate='CASCADE', ondelete='CASCADE')

    with op.batch_alter_table('fields', schema=None) as batch_op:
        batch_op.alter_column('location',
               existing_type=sa.Enum('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'trichy-home1', 'trichy-home2', 'house-yard', name='field_location'),
               type_=mysql.ENUM('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'house-yard', 'trichy-home1', 'trichy-home2'),
               existing_nullable=False)

    with op.batch_alter_table('yield', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', mysql.ENUM('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'trichy-home1', 'trichy-home2', 'house-yard'), nullable=True))
        batch_op.create_index('ix_yield_location', ['location'], unique=False)
        batch_op.create_foreign_key('yield_ibfk_2', 'fields', ['location'], ['location'], onupdate='CASCADE',
                                    ondelete='CASCADE')

    with op.batch_alter_table('sowing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', mysql.ENUM('tgudi', 'pallachi', 'potteri', 'pokonanthoki', 'mannamuti', 'trichy-home1', 'trichy-home2', 'house-yard'), nullable=True))
        batch_op.create_index('ix_sowing_location', ['location'], unique=False)
        batch_op.create_foreign_key('sowing_ibfk_1', 'fields', ['location'], ['location'], onupdate='CASCADE',
                                    ondelete='CASCADE')



    # ### end Alembic commands ###