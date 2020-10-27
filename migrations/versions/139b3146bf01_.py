"""empty message

Revision ID: 139b3146bf01
Revises: f6a0e5e4490a
Create Date: 2020-10-16 14:22:21.241863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '139b3146bf01'
down_revision = 'f6a0e5e4490a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mother_test_id', sa.Integer(), nullable=False),
    sa.Column('note_text', sa.String(length=2000), nullable=True),
    sa.Column('created_datetime', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('added_by', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['mother_test_id'], ['mother_test.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notes')
    # ### end Alembic commands ###