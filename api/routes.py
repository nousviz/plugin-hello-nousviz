"""
api/routes.py — Hello Nousviz Plugin

Complete route set exercising every plugin API pattern:
  - Health check
  - CRUD on items (list, create, update status, delete)
  - List events with pagination
  - All routes under /plugins/hello-nousviz/
  - Only queries tables declared in plugin.yaml
  - All SQL uses parameterised queries
  - No imports from other plugin modules
"""

from fastapi import APIRouter, HTTPException, Query
from apps.api.src.db import get_pg_conn

router = APIRouter()

SLUG = "hello-nousviz"
BASE = f"/plugins/{SLUG}"


@router.get(f"{BASE}/health-check")
async def health_check():
    """Verify the plugin's tables exist and are reachable."""
    try:
        with get_pg_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM hello_items")
            items = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM hello_events")
            events = cur.fetchone()[0]
        return {"status": "ok", "plugin": SLUG, "hello_items": items, "hello_events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@router.get(f"{BASE}/items")
async def list_items(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    status: str = Query(default=None),
):
    """List rows from hello_items with optional status filter."""
    with get_pg_conn() as conn:
        cur = conn.cursor()
        where = ""
        params: list = []
        if status:
            where = "WHERE status = %s"
            params.append(status)
        cur.execute(
            f"SELECT id, name, status, created_at FROM hello_items {where} "
            f"ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params + [limit, offset],
        )
        cols = [d[0] for d in cur.description]
        items = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.execute(f"SELECT count(*) FROM hello_items {where}", params)
        total = cur.fetchone()[0]
    return {"items": items, "total": total}


@router.post(f"{BASE}/items")
async def create_item(body: dict):
    """Create a test item. Body: {"name": str, "status": str (optional)}"""
    name = str(body.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    status = str(body.get("status", "active")).strip()
    if status not in ("active", "inactive"):
        raise HTTPException(status_code=400, detail="status must be 'active' or 'inactive'")
    try:
        with get_pg_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO hello_items (name, status) VALUES (%s, %s) "
                "RETURNING id, name, status, created_at",
                (name, status),
            )
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, cur.fetchone()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(f"{BASE}/items/{{item_id}}")
async def toggle_item(item_id: str, body: dict):
    """Toggle item status. Body: {"status": "active"|"inactive"}"""
    new_status = str(body.get("status", "")).strip()
    if new_status not in ("active", "inactive"):
        raise HTTPException(status_code=400, detail="status must be 'active' or 'inactive'")
    with get_pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE hello_items SET status = %s WHERE id = %s::uuid "
            "RETURNING id, name, status, created_at",
            (new_status, item_id),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    cols = ["id", "name", "status", "created_at"]
    return dict(zip(cols, row))


@router.delete(f"{BASE}/items/{{item_id}}")
async def delete_item(item_id: str):
    """Delete an item by ID."""
    with get_pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM hello_items WHERE id = %s::uuid RETURNING id",
            (item_id,),
        )
        deleted = cur.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": str(deleted[0])}


@router.get(f"{BASE}/events")
async def list_events(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    event_type: str = Query(default=None),
):
    """List rows from hello_events with optional type filter."""
    with get_pg_conn() as conn:
        cur = conn.cursor()
        where = ""
        params: list = []
        if event_type:
            where = "WHERE event_type = %s"
            params.append(event_type)
        cur.execute(
            f"SELECT id, event_type, detail, created_at FROM hello_events {where} "
            f"ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params + [limit, offset],
        )
        cols = [d[0] for d in cur.description]
        events = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.execute(f"SELECT count(*) FROM hello_events {where}", params)
        total = cur.fetchone()[0]
    return {"events": events, "total": total}
