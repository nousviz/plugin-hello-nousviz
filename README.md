# plugin-hello-nousviz

Ultimate skeleton [Nousviz](https://github.com/nousviz/nousviz) plugin. Exercises **every** plugin contract feature for end-to-end validation.

**This is not a product feature.** Install and uninstall freely. It exists to prove:

- Marketplace catalog shows the plugin and installs it
- SQL migrations create tables + seed sample data on install
- Plugin page renders Overview (manifest info) and Analytics (SQL panels) dashboards
- Settings tab renders configurable fields from the manifest and persists them
- Sync Now generates real data into plugin tables, respecting settings
- Alerts tab shows template alerts defined in the plugin's `alerts/` directory
- Data Port exposes tables with filters and pagination
- Datasets page shows plugin tables grouped by source
- Insights cards query plugin data
- Uninstall with "Remove tables" drops both tables cleanly

## Install

From the Nousviz marketplace, search for **Hello Nousviz** and click Install.

Or via API:
```bash
curl -X POST http://localhost:8000/api/plugins/hello-nousviz/install
```

## Verify

```bash
# Health check (routes active immediately — no restart needed)
curl http://localhost:8000/api/plugins/hello-nousviz/health-check

# List items (seeded on install)
curl http://localhost:8000/api/plugins/hello-nousviz/items

# Create an item
curl -X POST http://localhost:8000/api/plugins/hello-nousviz/items \
  -H "Content-Type: application/json" \
  -d '{"name": "my-test-item"}'

# Toggle status
curl -X PUT http://localhost:8000/api/plugins/hello-nousviz/items/{id} \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'

# Delete an item
curl -X DELETE http://localhost:8000/api/plugins/hello-nousviz/items/{id}

# List events
curl http://localhost:8000/api/plugins/hello-nousviz/events
```

## Structure

```
plugin-hello-nousviz/
├── plugin.yaml                        # Full manifest: identity, tables, nav, settings, sync, datasets
├── api/
│   └── routes.py                      # health-check, CRUD items, list events
├── src/
│   └── sync.py                        # Generates test data, reads settings, logs events
├── storage/
│   └── migrations/
│       ├── 001_initial.sql            # Creates hello_items + hello_events
│       ├── 001_initial_down.sql       # Drops both tables
│       ├── 002_seed.sql               # Sample data (10 items, 5 events)
│       └── 002_seed_down.sql          # Removes sample data
├── dashboards/
│   ├── overview.yaml                  # Plugin info tab (type: plugin_info)
│   └── analytics.yaml                 # SQL stat + table panels
├── alerts/
│   ├── no-recent-items.yaml           # Alert: no items created in 24h
│   ├── high-inactive-ratio.yaml       # Alert: >50% items inactive
│   └── sync-failure.yaml              # Alert: no sync in 48h
├── datasets/
│   ├── hello_items.yaml               # Table schema + description
│   └── hello_events.yaml              # Table schema + description
├── dataport.yaml                      # Data Port tabs with filters
├── insights.yaml                      # Insight cards (total items, today, last sync)
└── README.md
```

## Features exercised

| Feature | File | What it proves |
|---------|------|----------------|
| Install + migrations | `storage/migrations/` | Tables created, seed data inserted |
| Route hot-loading | `api/routes.py` | Routes active without API restart |
| Dashboard rendering | `dashboards/*.yaml` | SQL panels render real data |
| Plugin overview | `dashboards/overview.yaml` | Manifest info tab |
| Settings persistence | `plugin.yaml` settings | Form renders, values persist in DB |
| Sync with real data | `src/sync.py` | Reads settings, generates items, logs events |
| Alert templates | `alerts/*.yaml` | Pre-built alerts from plugin manifest |
| Data Port | `dataport.yaml` | Table browsing with filters |
| Datasets | `datasets/*.yaml` | Grouped in datasets page |
| Insights | `insights.yaml` | Insight cards from plugin queries |
| Uninstall | `001_initial_down.sql` | Clean table removal |

## Plugin contract

This plugin follows the [Nousviz plugin architecture spec](https://github.com/nousviz/nousviz/blob/main/docs/plugin-architecture.md).

- No external connections required (Postgres only)
- Only reads/writes `hello_items` and `hello_events`
- All SQL is parameterised
- All Postgres connections use `with get_pg_conn() as conn:` context manager
