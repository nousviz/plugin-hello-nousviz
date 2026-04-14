-- hello-nousviz: 002_seed
-- Inserts sample data so the plugin has something to show immediately after install.
-- Idempotent — uses ON CONFLICT DO NOTHING for items (unique name constraint).

INSERT INTO hello_items (name, status) VALUES
    ('alpha-beacon-001',  'active'),
    ('beta-prism-017',    'active'),
    ('gamma-orbit-042',   'active'),
    ('delta-nexus-099',   'inactive'),
    ('epsilon-spark-123', 'active'),
    ('zeta-atlas-256',    'active'),
    ('eta-cedar-314',     'inactive'),
    ('theta-flame-500',   'active'),
    ('iota-grain-777',    'active'),
    ('kappa-pixel-999',   'inactive')
ON CONFLICT (name) DO NOTHING;

INSERT INTO hello_events (event_type, detail) VALUES
    ('install',  '{"source": "seed", "version": "1.2.0"}'),
    ('sync_run', '{"items_created": 10, "elapsed_ms": 42, "timestamp": "2026-04-14T00:00:00Z"}'),
    ('sync_run', '{"items_created": 5, "elapsed_ms": 28, "timestamp": "2026-04-14T04:00:00Z"}'),
    ('sync_run', '{"items_created": 3, "elapsed_ms": 15, "timestamp": "2026-04-14T08:00:00Z"}'),
    ('error',    '{"message": "Simulated error for testing alert templates"}');
