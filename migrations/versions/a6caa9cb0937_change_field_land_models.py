"""change field land models

Revision ID: a6caa9cb0937
Revises: 3b7761a5f815
Create Date: 2022-12-14 18:02:15.225305

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a6caa9cb0937'
down_revision = '3b7761a5f815'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fieldmodel')
    with op.batch_alter_table('fields', schema=None) as batch_op:
        batch_op.drop_index('ix_fields_nickname')
        batch_op.drop_column('nickname')
        batch_op.drop_column('survey')
        batch_op.drop_column('geotag')
        batch_op.drop_column('owner')
        batch_op.drop_column('deed')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fields', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deed', mysql.VARCHAR(length=10), nullable=True))
        batch_op.add_column(sa.Column('owner', mysql.VARCHAR(length=30), nullable=True))
        batch_op.add_column(sa.Column('geotag', mysql.VARCHAR(length=30), nullable=True))
        batch_op.add_column(sa.Column('survey', mysql.VARCHAR(length=10), nullable=True))
        batch_op.add_column(sa.Column('nickname', mysql.VARCHAR(length=10), nullable=False))
        batch_op.create_index('ix_fields_nickname', ['nickname'], unique=False)

    op.create_table('fieldmodel',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
