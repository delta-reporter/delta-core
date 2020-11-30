"""empty message

Revision ID: 39f3a90b4103
Revises: 139b3146bf01
Create Date: 2020-11-30 10:21:04.546700

"""
from alembic import op
from sqlalchemy import orm
import sqlalchemy as sa
import models


# revision identifiers, used by Alembic.
revision = "39f3a90b4103"
down_revision = "139b3146bf01"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "smart_link_location",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "smart_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filtered", sa.Boolean(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("environment", sa.String(length=2000), nullable=True),
        sa.Column("smart_link", sa.String(), nullable=True),
        sa.Column("datetime_format", sa.String(length=300), nullable=True),
        sa.Column("label", sa.String(length=30), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["smart_link_location.id"],),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("test", sa.Column("data", sa.JSON(), nullable=True))
    op.add_column(
        "test_run", sa.Column("environment", sa.String(length=2000), nullable=True)
    )
    # ### end Alembic commands ###

    # ### initialise smart link tables ###

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    session.add(models.SmartLinkLocation(name="Test"))
    session.add(models.SmartLinkLocation(name="Test Run"))

    session.commit()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("test_run", "environment")
    op.drop_column("test", "data")
    op.drop_table("smart_links")
    op.drop_table("smart_link_location")
    # ### end Alembic commands ###