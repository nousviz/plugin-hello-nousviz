"""
sync.py — Hello Nousviz sync script

Demonstrates the full sync contract:
  1. Reads plugin settings from the platform API
  2. Checks sync_enabled — exits early if disabled
  3. Generates random test items (count from item_limit setting)
  4. Logs a sync event to hello_events (event_type from event_label setting)
  5. Updates _last_sync in plugin_settings
  6. Exits 0 on success, 1 on failure

Called by: POST /api/plugins/hello-nousviz/sync
Schedule: every 4 hours (see plugin.yaml sync.schedule)
Can also be run directly: python3 src/sync.py
"""

import os
import sys
import json
import random
import string
import logging
import time
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="[hello-nousviz sync] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.insert(0, REPO_ROOT)

ADJECTIVES = [
    "red", "blue", "fast", "slow", "big", "tiny", "bold", "calm",
    "dark", "keen", "warm", "cool", "wild", "soft", "raw", "dry",
]
NOUNS = [
    "falcon", "beacon", "prism", "orbit", "nexus", "spark", "delta",
    "atlas", "cedar", "flame", "grain", "pixel", "raven", "storm",
]


def random_name():
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    suffix = "".join(random.choices(string.digits, k=3))
    return f"{adj}-{noun}-{suffix}"


def load_settings(conn):
    """Load saved settings, merged with defaults."""
    defaults = {
        "sync_enabled": True,
        "item_limit": 5,
        "event_label": "sync_run",
    }
    cur = conn.cursor()
    cur.execute(
        "SELECT key, value FROM plugin_settings WHERE plugin_id = 'hello-nousviz'"
    )
    for key, value in cur.fetchall():
        if key.startswith("_"):
            continue
        defaults[key] = value
    return defaults


def run():
    start = time.time()
    try:
        from apps.api.src.db import get_pg_conn

        with get_pg_conn() as conn:
            settings = load_settings(conn)
            cur = conn.cursor()

            # Check sync_enabled
            if not settings.get("sync_enabled", True):
                logger.info("Sync disabled in settings — skipping")
                return True

            item_limit = int(settings.get("item_limit", 5))
            event_label = str(settings.get("event_label", "sync_run"))

            # Generate items
            created = 0
            for _ in range(item_limit):
                name = random_name()
                status = random.choice(["active", "active", "active", "inactive"])
                try:
                    cur.execute(
                        "INSERT INTO hello_items (name, status) VALUES (%s, %s)",
                        (name, status),
                    )
                    created += 1
                except Exception:
                    # Name collision (UNIQUE constraint) — skip
                    conn.rollback()
                    continue

            elapsed_ms = int((time.time() - start) * 1000)
            now = datetime.now(timezone.utc)

            # Log sync event
            detail = {
                "timestamp": now.isoformat(),
                "items_created": created,
                "item_limit": item_limit,
                "elapsed_ms": elapsed_ms,
            }
            cur.execute(
                "INSERT INTO hello_events (event_type, detail) VALUES (%s, %s) RETURNING id",
                (event_label, json.dumps(detail)),
            )
            event_id = cur.fetchone()[0]

            # Update last sync timestamp
            cur.execute(
                """
                INSERT INTO plugin_settings (plugin_id, key, value, updated_at)
                VALUES ('hello-nousviz', '_last_sync', %s::jsonb, now())
                ON CONFLICT (plugin_id, key)
                DO UPDATE SET value = EXCLUDED.value, updated_at = now()
                """,
                (json.dumps({"timestamp": now.isoformat()}),),
            )
            conn.commit()

        logger.info(
            f"Sync complete — {created}/{item_limit} items created, "
            f"event={event_id}, {elapsed_ms}ms"
        )
        return True
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return False


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
