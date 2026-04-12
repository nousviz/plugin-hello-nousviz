"""
api/routes.py — Hello Nousviz Plugin

Minimal route set for validating the Nousviz plugin install loop.
Exercises: route registration, health-check, Postgres query, parameterised SQL.

Rules enforced here (see docs/plugin-architecture.md):
  - All routes under /plugins/hello-nousviz/
  - Only queries tables declared in plugin.yaml: hello_items, hello_events
  - All connections use `with get_pg_conn() as conn:` — context manager handles
    pool return, commit on success, rollback on exception automatically
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
    """
    Verify the plugin's tables exist and are reachable.
    Called by the marketplace Configure page and the E2E test suite.
    Returns 200 {"status": "ok"} if tables exist, 500 if not.
    """
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
):
    """List rows from hello_items."""
    with get_pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, status, created_at "
            "FROM hello_items "
            "ORDER BY created_at DESC "
            "LIMIT %s OFFSET %s",
            (limit, offset),
        )
        cols = [d[0] for d in cur.description]
        items = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.execute("SELECT count(*) FROM hello_items")
        total = cur.fetchone()[0]
    return {"items": items, "total": total}


@router.post(f"{BASE}/items")
async def create_item(body: dict):
    """
    Create a test item. Used by the E2E test suite to verify write access.
    Body: {"name": str}
    """
    name = str(body.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    try:
        with get_pg_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO hello_items (name) VALUES (%s) RETURNING id, name, status, created_at",
                (name,),
            )
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, cur.fetchone()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
