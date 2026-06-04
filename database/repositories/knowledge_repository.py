from datetime import UTC, datetime
import json
from uuid import uuid5, NAMESPACE_URL

from database.db import get_connection


def make_chunk_id(source, content_hash, tenant_id="TENANT_DEFAULT"):
    return f"KNOW_{uuid5(NAMESPACE_URL, f'{tenant_id}:{source}:{content_hash}').hex[:12].upper()}"


def upsert_knowledge_chunk(
    source,
    title,
    content,
    content_hash,
    embedding,
    tenant_id="TENANT_DEFAULT",
):
    chunk_id = make_chunk_id(source, content_hash, tenant_id=tenant_id)
    now = datetime.now(UTC).isoformat()
    query = """
    INSERT INTO knowledge_chunks (
        chunk_id,
        tenant_id,
        source,
        title,
        content,
        content_hash,
        embedding_json,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT (tenant_id, source, content_hash)
    DO UPDATE SET
        title = EXCLUDED.title,
        content = EXCLUDED.content,
        embedding_json = EXCLUDED.embedding_json,
        updated_at = EXCLUDED.updated_at
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (
                chunk_id,
                tenant_id,
                source,
                title,
                content,
                content_hash,
                json.dumps(embedding),
                now,
                now,
            ),
        )
        connection.commit()

    return get_knowledge_chunk_by_id(chunk_id)


def get_knowledge_chunk_by_id(chunk_id):
    query = "SELECT * FROM knowledge_chunks WHERE chunk_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (chunk_id,)).fetchone()

    if row is None:
        return None

    return deserialize_chunk(dict(row))


def list_knowledge_chunks(tenant_id="TENANT_DEFAULT"):
    query = """
    SELECT *
    FROM knowledge_chunks
    WHERE tenant_id = ?
    ORDER BY source ASC, title ASC, chunk_id ASC
    """

    with get_connection() as connection:
        rows = connection.execute(query, (tenant_id,)).fetchall()

    return [deserialize_chunk(dict(row)) for row in rows]


def delete_stale_knowledge_chunks(active_chunk_ids, tenant_id="TENANT_DEFAULT"):
    if not active_chunk_ids:
        return 0

    placeholders = ", ".join(["?"] * len(active_chunk_ids))
    query = f"""
    DELETE FROM knowledge_chunks
    WHERE tenant_id = ? AND chunk_id NOT IN ({placeholders})
    """

    with get_connection() as connection:
        cursor = connection.execute(query, (tenant_id, *active_chunk_ids))
        connection.commit()

    return cursor.rowcount


def deserialize_chunk(chunk):
    embedding = chunk.get("embedding_json", "[]")
    if isinstance(embedding, str):
        chunk["embedding"] = json.loads(embedding)
    else:
        chunk["embedding"] = embedding
    return chunk
