"""change account link table name

Revision ID: 2e6ba70a5afc
Revises: 60c4474e0a49
Create Date: 2023-01-31 16:32:15.163493

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2e6ba70a5afc'
down_revision = '60c4474e0a49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('accounts_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts_link',
    sa.Column('entry_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('accounts_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['accounts_id'], ['accounts.id'], name='accounts_link_ibfk_3'),
    sa.ForeignKeyConstraint(['entry_id'], ['entry.id'], name='accounts_link_ibfk_2'),
    sa.PrimaryKeyConstraint('entry_id', 'accounts_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
