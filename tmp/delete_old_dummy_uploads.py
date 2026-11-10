"""Remove only the four older dummy handbook uploads after strict preflight checks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pinecone import Pinecone

from app.aws import client as aws_client
from app.config import settings
from app.db import connection, audit


TITLE = "dummy_company_handbook.pdf"
TENANT = "demo-workspace"
KEEP_ID = "2aa75a08-2437-4016-a206-bf8ee9e68802"
DELETE_IDS = {
    "4bcc48fa-0ad5-42a9-b26a-f6027d4dd9ce",
    "8159715f-0169-4d65-814c-bc4794136270",
    "f36ab5e5-e478-4134-af86-e3a556b09fd8",
    "47443fc8-fb1f-4735-982b-9837641ee13f",
}


def main():
    s = settings()
    if not s.s3_bucket:
        raise RuntimeError("S3_BUCKET is unset; refusing to delete anything")
    if not s.pinecone_api_key or not s.pinecone_index_name:
        raise RuntimeError("Pinecone settings are incomplete; refusing to delete anything")

    with connection() as conn:
        rows = conn.execute(
            """SELECT id::text AS id, title, status, created_at, s3_key, tenant_id
               FROM documents
               WHERE tenant_id = %s AND title = %s
               ORDER BY created_at DESC
               FOR UPDATE""",
            (TENANT, TITLE),
        ).fetchall()
        ids = [row["id"] for row in rows]
        if len(rows) != 5 or ids[0] != KEEP_ID or set(ids[1:]) != DELETE_IDS:
            raise RuntimeError("Dummy document set changed since inspection; nothing deleted")
        if any(row["status"] not in {"ready", "pending", "failed"} for row in rows[1:]):
            raise RuntimeError("An older dummy upload is processing; nothing deleted")
        employee_before = conn.execute(
            "SELECT count(*) AS n FROM documents WHERE tenant_id = %s AND title = %s",
            (TENANT, "01_employee_handbook.pdf"),
        ).fetchone()["n"]
        if employee_before < 1:
            raise RuntimeError("Expected employee handbook row is missing; nothing deleted")

        pc = Pinecone(api_key=s.pinecone_api_key)
        info = pc.describe_index(s.pinecone_index_name)
        if int(info.dimension) != s.embed_dim or str(info.metric).lower() != "cosine":
            raise RuntimeError("Pinecone index does not match configured dimension/metric; nothing deleted")
        vector_index = pc.Index(s.pinecone_index_name)
        s3 = aws_client("s3")

        for row in rows[1:]:
            # Metadata filter targets only vectors belonging to this exact document.
            vector_index.delete(
                namespace="tenant-" + TENANT,
                filter={"document_id": {"$eq": row["id"]}},
            )
            # Delete only the unique S3 object key recorded on this exact document row.
            s3.delete_object(Bucket=s.s3_bucket, Key=row["s3_key"])

        deleted = conn.execute(
            """DELETE FROM documents
               WHERE tenant_id = %s AND title = %s AND id = ANY(%s::uuid[])
               RETURNING id::text AS id""",
            (TENANT, TITLE, list(DELETE_IDS)),
        ).fetchall()
        if {row["id"] for row in deleted} != DELETE_IDS:
            raise RuntimeError("Database delete count/IDs did not match preflight; transaction rolled back")
        for row in rows[1:]:
            audit(conn, "local-admin", TENANT, "dummy_duplicate_removed", {
                "document_id": row["id"], "title": TITLE, "status": row["status"]
            })

    with connection() as conn:
        remaining = conn.execute(
            """SELECT id::text AS id, status FROM documents
               WHERE tenant_id = %s AND title = %s ORDER BY created_at DESC""",
            (TENANT, TITLE),
        ).fetchall()
        employee_after = conn.execute(
            "SELECT count(*) AS n FROM documents WHERE tenant_id = %s AND title = %s",
            (TENANT, "01_employee_handbook.pdf"),
        ).fetchone()["n"]
    if len(remaining) != 1 or remaining[0]["id"] != KEEP_ID or employee_after != employee_before:
        raise RuntimeError("Post-delete verification failed; inspect document records")
    print(f"Removed {len(DELETE_IDS)} older dummy uploads and their S3/Pinecone data.")
    print(f"Retained newest dummy upload {KEEP_ID} ({remaining[0]['status']}).")
    print(f"Employee handbook rows preserved: {employee_after}.")


if __name__ == "__main__":
    main()
