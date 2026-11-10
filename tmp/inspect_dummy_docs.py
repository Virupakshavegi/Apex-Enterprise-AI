import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connection

with connection() as conn:
    rows = conn.execute("""
        SELECT id::text AS id, title, status, created_at::text AS created_at,
               s3_key, tenant_id
        FROM documents
        WHERE title = 'dummy_company_handbook.pdf'
        ORDER BY created_at DESC
    """).fetchall()
    for row in rows:
        print(row)
