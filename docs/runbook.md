# Local runbook

## Run

```bash
python -m unittest discover -s tests -v
python -m app.demo
```

Expected demo: 2 delivered messages and two fictional fulfilment records.

## Debug

- Check Python 3.10+.
- Run from repository root.
- No network access or credentials required.
- Data defaults to SQLite in-memory and is discarded on exit.

## Production readiness gaps

An actual deployment would require authenticated HTTP adapters, hosted queues, durable relational storage, correlation IDs, distributed retries, DLQ tooling, dead-letter re-drive approval, concurrency claims, telemetry, recovery drills, cost analysis and infrastructure-as-code.
