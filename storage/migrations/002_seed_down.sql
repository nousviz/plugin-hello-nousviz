-- hello-nousviz: 002_seed_down
-- Removes seeded sample data. Does not drop tables (that's 001_initial_down).

DELETE FROM hello_items WHERE name IN (
    'alpha-beacon-001', 'beta-prism-017', 'gamma-orbit-042',
    'delta-nexus-099', 'epsilon-spark-123', 'zeta-atlas-256',
    'eta-cedar-314', 'theta-flame-500', 'iota-grain-777', 'kappa-pixel-999'
);

DELETE FROM hello_events WHERE detail->>'source' = 'seed';
DELETE FROM hello_events WHERE detail->>'message' = 'Simulated error for testing alert templates';
