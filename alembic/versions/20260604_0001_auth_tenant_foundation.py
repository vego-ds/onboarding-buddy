"""auth tenant foundation

Revision ID: 20260604_0001
Revises:
Create Date: 2026-06-04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260604_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenants",
        sa.Column("tenant_id", sa.Text(), primary_key=True),
        sa.Column("tenant_name", sa.Text(), nullable=False),
        sa.Column("tenant_domain", sa.Text(), unique=True),
        sa.Column("sso_provider", sa.Text()),
        sa.Column("sso_issuer", sa.Text()),
        sa.Column("sso_audience", sa.Text()),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
    )
    op.execute(
        """
        INSERT INTO tenants (tenant_id, tenant_name, created_at, updated_at)
        VALUES ('TENANT_DEFAULT', 'Default Tenant', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (tenant_id) DO NOTHING
        """
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("refresh_token_id", sa.Text(), primary_key=True),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("expires_at", sa.Text(), nullable=False),
        sa.Column("revoked_at", sa.Text()),
        sa.Column("created_at", sa.Text(), nullable=False),
    )
    op.create_table(
        "password_reset_tokens",
        sa.Column("reset_token_id", sa.Text(), primary_key=True),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("expires_at", sa.Text(), nullable=False),
        sa.Column("used_at", sa.Text()),
        sa.Column("created_at", sa.Text(), nullable=False),
    )
    op.create_table(
        "auth_audit_logs",
        sa.Column("auth_audit_id", sa.Text(), primary_key=True),
        sa.Column("tenant_id", sa.Text()),
        sa.Column("user_id", sa.Text()),
        sa.Column("email", sa.Text()),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("event_status", sa.Text(), nullable=False),
        sa.Column("event_message", sa.Text(), nullable=False),
        sa.Column("ip_address", sa.Text()),
        sa.Column("user_agent", sa.Text()),
        sa.Column("created_at", sa.Text(), nullable=False),
    )
    op.add_column("users", sa.Column("tenant_id", sa.Text(), nullable=False, server_default="TENANT_DEFAULT"))
    op.create_index("idx_users_tenant_id", "users", ["tenant_id"])


def downgrade():
    op.drop_index("idx_users_tenant_id", table_name="users")
    op.drop_column("users", "tenant_id")
    op.drop_table("auth_audit_logs")
    op.drop_table("password_reset_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("tenants")
