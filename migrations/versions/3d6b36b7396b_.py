"""empty message

Revision ID: 3d6b36b7396b
Revises: d31320fd769e
Create Date: 2020-06-02 08:34:49.984422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3d6b36b7396b"
down_revision = "d31320fd769e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "test_retries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("test_history_id", sa.Integer(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=True),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("trace", sa.String(), nullable=True),
        sa.Column("message", sa.String(length=2000), nullable=True),
        sa.Column("error_type", sa.String(length=2000), nullable=True),
        sa.ForeignKeyConstraint(["test_history_id"], ["test_history.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("test_retries")
    # ### end Alembic commands ###