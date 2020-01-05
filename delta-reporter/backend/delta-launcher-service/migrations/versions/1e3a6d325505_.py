"""empty message

Revision ID: 1e3a6d325505
Revises: 
Create Date: 2020-01-05 18:52:53.526626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e3a6d325505'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('launches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_resolution',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_suite_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_suites',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('start_datetime', sa.DateTime(), nullable=False),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('test_type_id', sa.Integer(), nullable=False),
    sa.Column('test_suite_status_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['test_suite_status_id'], ['test_suite_status.id'], ),
    sa.ForeignKeyConstraint(['test_type_id'], ['test_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('start_datetime', sa.DateTime(), nullable=False),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.Column('resolution_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['resolution_id'], ['test_resolution.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['test_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tests')
    op.drop_table('test_suites')
    op.drop_table('test_type')
    op.drop_table('test_suite_status')
    op.drop_table('test_status')
    op.drop_table('test_resolution')
    op.drop_table('projects')
    op.drop_table('project_status')
    op.drop_table('launches')
    # ### end Alembic commands ###
