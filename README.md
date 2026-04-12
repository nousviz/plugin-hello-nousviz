# plugin-hello-nousviz

Bare-bones [Nousviz](https://github.com/nousviz/nousviz) plugin for validating the end-to-end plugin install loop.

**This is not a product feature.** Install and uninstall freely. It exists to prove:

- Marketplace catalog shows the plugin
- Install clones this repo and hot-loads the routes (no API restart required)
- SQL migrations create `hello_items` and `hello_events` tables on install
- Plugin page renders the Overview dashboard via `GenericPluginPage`
- Data Port exposes `hello_items` and `hello_events`
- Uninstall with "Remove tables" drops both tables cleanly

## Install

From the Nousviz marketplace, search for **Hello Nousviz** and click Install.

Or via API:
```bash
curl -X POST http://localhost:8000/api/plugins/hello-nousviz/install
```

## Verify

```bash
# Routes active immediately (no restart needed)
curl http://localhost:8000/api/plugins/hello-nousviz/health-check
# → {"status": "ok", "hello_items": 0, "hello_events": 0}

# Create a test item
curl -X POST http://localhost:8000/api/plugins/hello-nousviz/items \
  -H "Content-Type: application/json" \
  -d '{"name": "test-item"}'

# List items
curl http://localhost:8000/api/plugins/hello-nousviz/items
```

## Structure

```
plugin-hello-nousviz/
├── plugin.yaml                      # Manifest: identity, tables, dashboard, nav
├── api/
│   └── routes.py                    # health-check, list items, create item
├── storage/
│   └── migrations/
│       ├── 001_initial.sql          # Creates hello_items + hello_events
│       └── 001_initial_down.sql     # Drops both tables (used on uninstall)
├── dashboards/
│   └── overview.yaml                # Stat + table panels
└── dataport.yaml                    # Exposes tables to Data Port page
```

## Plugin contract

This plugin follows the [Nousviz plugin architecture spec](https://github.com/nousviz/nousviz/blob/main/docs/plugin-architecture.md).

- No external connections required
- Only reads/writes `hello_items` and `hello_events`
- All SQL is parameterised
- All Postgres connections use `try/finally: conn.close()`
