"""empty message

Revision ID: d31320fd769e
Revises: 636c5796f80a
Create Date: 2020-05-30 21:18:02.318093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d31320fd769e"
down_revision = "636c5796f80a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "test_history", sa.Column("parameters", sa.String(length=3000), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("test_history", "parameters")
    # ### end Alembic commands ###