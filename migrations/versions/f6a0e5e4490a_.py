"""empty message

Revision ID: f6a0e5e4490a
Revises: 7fbc4dda2333
Create Date: 2020-10-01 17:41:05.962900

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f6a0e5e4490a"
down_revision = "7fbc4dda2333"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("test", "mother_test")
    op.execute("ALTER SEQUENCE test_id_seq RENAME TO mother_test_id_seq")
    op.execute("ALTER INDEX test_pkey RENAME TO mother_test_pkey")
    op.execute(
        'ALTER TABLE mother_test RENAME CONSTRAINT "test_test_resolution_id_fkey" TO "mother_test_test_resolution_id_fkey"'
    )
    op.execute(
        'ALTER TABLE mother_test RENAME CONSTRAINT "test_test_suite_id_fkey" TO "mother_test_test_suite_id_fkey"'
    )

    op.rename_table("test_history", "test")
    op.execute("ALTER SEQUENCE test_history_id_seq RENAME TO test_id_seq")
    op.execute("ALTER INDEX test_history_pkey RENAME TO test_pkey")
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_history_test_id_fkey" TO "test_mother_test_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_history_test_resolution_id_fkey" TO "test_test_resolution_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_history_test_run_id_fkey" TO "test_test_run_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_history_test_status_id_fkey" TO "test_test_status_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_history_test_suite_history_id_fkey" TO "test_test_suite_history_id_fkey"'
    )

    op.execute(
        'ALTER TABLE test_retries RENAME CONSTRAINT "test_retries_test_history_id_fkey" TO "test_retries_test_id_fkey"'
    )

    op.alter_column("test_retries", "test_history_id", new_column_name="test_id")
    op.alter_column("test", "test_id", new_column_name="mother_test_id")


def downgrade():

    op.execute("ALTER SEQUENCE test_id_seq RENAME TO test_history_id_seq")
    op.execute("ALTER INDEX test_pkey RENAME TO test_history_pkey")
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_mother_test_id_fkey" TO "test_history_test_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_test_resolution_id_fkey" TO "test_history_test_resolution_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_test_run_id_fkey" TO "test_history_test_run_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_test_status_id_fkey" TO "test_history_test_status_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "test_test_suite_history_id_fkey" TO "test_history_test_suite_history_id_fkey"'
    )
    op.rename_table("test", "test_history")

    op.rename_table("mother_test", "test")
    op.execute("ALTER SEQUENCE mother_test_id_seq RENAME TO test_id_seq")
    op.execute("ALTER INDEX mother_test_pkey RENAME TO test_pkey")
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "mother_test_test_resolution_id_fkey" TO "test_test_resolution_id_fkey"'
    )
    op.execute(
        'ALTER TABLE test RENAME CONSTRAINT "mother_test_test_suite_id_fkey" TO "test_test_suite_id_fkey"'
    )

    op.execute(
        'ALTER TABLE test_retries RENAME CONSTRAINT "test_retries_test_id_fkey" TO "test_retries_test_history_id_fkey"'
    )

    op.alter_column("test_retries", "test_id", new_column_name="test_history_id")
    op.alter_column("test_history", "mother_test_id", new_column_name="test_id")
    op.alter_column("test_history", "mother_test", new_column_name="test")
