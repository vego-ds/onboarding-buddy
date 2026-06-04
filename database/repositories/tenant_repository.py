from datetime import UTC, datetime
from uuid import uuid4

from database.db import get_connection


def create_tenant(tenant_name, tenant_domain=None, sso_provider=None, sso_issuer=None, sso_audience=None):
    tenant_id = f"TENANT_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()
    query = """
    INSERT INTO tenants (
        tenant_id,
        tenant_name,
        tenant_domain,
        sso_provider,
        sso_issuer,
        sso_audience,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (
                tenant_id,
                tenant_name,
                tenant_domain,
                sso_provider,
                sso_issuer,
                sso_audience,
                now,
                now,
            ),
        )
        connection.commit()

    return get_tenant_by_id(tenant_id)


def get_tenant_by_id(tenant_id):
    query = "SELECT * FROM tenants WHERE tenant_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (tenant_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_tenant_by_domain(domain):
    query = "SELECT * FROM tenants WHERE tenant_domain = ?"

    with get_connection() as connection:
        row = connection.execute(query, (str(domain or "").lower(),)).fetchone()

    if row is None:
        return None

    return dict(row)
