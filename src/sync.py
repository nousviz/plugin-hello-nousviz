"""
sync.py — Hello Nousviz sync script

Minimal sync implementation demonstrating the sync contract:
  - Inserts a sync_run event into hello_events
  - Updates _last_sync in plugin_settings for the settings tab
  - Logs result to stdout
  - Exits 0 on success, 1 on failure

Called by: POST /api/plugins/hello-nousviz/sync
Can also be run directly: python3 src/sync.py
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="[hello-nousviz sync] %(message)s")
logger = logging.getLogger(__name__)

# Add repo root to path so we can import from apps/
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.insert(0, REPO_ROOT)


def run():
    try:
        from apps.api.src.db import get_pg_conn
        now = datetime.now(timezone.utc)
        with get_pg_conn() as conn:
            cur = conn.cursor()
            # Insert sync event
            cur.execute(
                "INSERT INTO hello_events (event_type, detail) VALUES (%s, %s) RETURNING id",
                ("sync_run", json.dumps({"timestamp": now.isoformat()}))
            )
            event_id = cur.fetchone()[0]
            # Update last sync timestamp in plugin_settings
            cur.execute(
                """
                INSERT INTO plugin_settings (plugin_id, key, value, updated_at)
                VALUES ('hello-nousviz', '_last_sync', %s::jsonb, now())
                ON CONFLICT (plugin_id, key)
                DO UPDATE SET value = EXCLUDED.value, updated_at = now()
                """,
                (json.dumps({"timestamp": now.isoformat()}),)
            )
            conn.commit()
        logger.info(f"Sync complete — event id={event_id}, at={now.isoformat()}")
        return True
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return False


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
