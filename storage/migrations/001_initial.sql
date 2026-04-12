-- hello-nousviz: 001_initial
-- Creates the plugin's two tables.
--
-- Rules:
--   USE CREATE TABLE IF NOT EXISTS (idempotent — safe to run twice)
--   Table names prefixed with hello_ to avoid collisions with core tables
--   All tables listed here must also appear in plugin.yaml databases.postgres.tables
--   Every table here must have a matching DROP in 001_initial_down.sql

CREATE TABLE IF NOT EXISTS hello_items (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL UNIQUE,
    status      TEXT        NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'inactive')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS hello_items_status_idx     ON hello_items(status);
CREATE INDEX IF NOT EXISTS hello_items_created_at_idx ON hello_items(created_at DESC);


CREATE TABLE IF NOT EXISTS hello_events (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type  TEXT        NOT NULL,
    detail      JSONB       NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS hello_events_type_idx    ON hello_events(event_type);
CREATE INDEX IF NOT EXISTS hello_events_created_idx ON hello_events(created_at DESC);
