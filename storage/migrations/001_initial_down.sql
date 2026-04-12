-- hello-nousviz: 001_initial_down
-- Reverses 001_initial.sql exactly.
-- Run automatically when the operator uninstalls this plugin with "Remove tables" selected.
--
-- Rules:
--   USE DROP TABLE IF EXISTS (idempotent)
--   Drop indexes before tables
--   Drop in reverse order of creation

DROP INDEX IF EXISTS hello_events_created_idx;
DROP INDEX IF EXISTS hello_events_type_idx;
DROP TABLE IF EXISTS hello_events;

DROP INDEX IF EXISTS hello_items_created_at_idx;
DROP INDEX IF EXISTS hello_items_status_idx;
DROP TABLE IF EXISTS hello_items;
