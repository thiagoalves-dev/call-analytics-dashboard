# Architecture

![Architecture diagram](architecture.png)

## The pieces

| Service | What it is | Why |
|---|---|---|
| `frontend` | Vue 3 + Vite, built to static files and served by nginx | nginx also proxies `/api`, so the browser talks to one origin: the session cookie works without CORS, and SSE goes through with buffering off. |
| `api` | FastAPI, 2 uvicorn worker processes | API-first, async, OpenAPI docs at `/docs`. Two workers on purpose: it proves live events reach a browser no matter which process handled the ingest. |
| `db` | PostgreSQL 17 + TimescaleDB (Community edition, free) | Calls are append-only time-series. Timescale gives automatic time partitioning and incremental rollups on top of plain Postgres. |
| `redis` | Redis pub/sub | Fan-out of new calls to every API process. |
| `simulator` | A small Python service | Stands in for the telephony provider. Sends finished calls to `POST /api/calls`, the same way a webhook would. |
| `setup` | One-shot container | Runs the Alembic migrations, then seeds demo data if the database is empty. |

## Data flow

**Live path.** simulator → `POST /api/calls` (API key) → insert into `calls` → publish to Redis channel
`calls:<account_id>` → every API process receives it → pushed to that account's open browsers over
Server-Sent Events → the browser collects new calls and, every 10 seconds, adds them to the feed and refetches
the charts. The page says so at the top.

**Read path.** The charts read `call_stats_hourly`, never the raw table. The live feed reads the 50 calls
that ended most recently through the `(account_id, ended_at DESC)` index. It orders by `ended_at`, not
`started_at`, because a call is reported when it ends: a 10-minute call that just finished belongs at the top.

**Backfill path.** The historical seed skips the API and generates rows inside Postgres
(`INSERT … SELECT generate_series`), one day at a time. Bulk backfill and live ingestion are separate paths
on purpose: loading millions of rows through HTTP would take hours.

## Data model

- `accounts` — the tenant. Holds the IANA timezone used to cut daily buckets.
- `users` — people who log in. Belong to one account.
- `api_keys` — machine credentials for ingestion. Only the SHA-256 of the key is stored.
- `campaigns` — each owns a tracking number. A call to that number belongs to that campaign, the way call
  tracking attributes calls.
- `calls` — one row per finished call. A hypertable partitioned by `started_at` in 1-day chunks. `ended_at`
  (start + duration) is stored so the feed can sort by it with an index.
- `call_stats_hourly` — the continuous aggregate: per account, campaign and hour, one counter per outcome.

## Decisions and why

### Multi-tenancy: shared tables, `account_id` everywhere

Every tenant-owned table carries `account_id`, every hot index starts with it, and the API takes the
account only from the signed JWT or the API key, never from the URL. This is the pool model most SaaS
products use. A query for one account only reads that account's slice of the index, so a 100M-row table
behaves like a small one for a typical customer. It also makes sharding by `account_id` possible later
without a rewrite.

### TimescaleDB continuous aggregate

- **Hypertable, 1-day chunks.** "Last 7 days" only touches 7–8 chunks. Old data can later be compressed or
  dropped a chunk at a time.
- **`materialized_only = false` (real-time aggregation).** Rows newer than the last refresh are aggregated on
  the fly and merged with the materialized buckets, so the current hour is always live.
- **Refresh policy: every 5 minutes, from 3 days ago to 1 hour ago.** The 3-day start picks up late calls;
  the 1-hour end leaves the in-progress hour to real-time aggregation instead of materializing a bucket that
  is still changing.
- **Daily view = re-bucketed hourly rows in the account's timezone.** `time_bucket('1 day', bucket, tz)` on
  the hourly aggregate. Works because the supported timezones have whole-hour offsets; a +05:30 zone would
  need a 30-minute aggregate.
- **Trade-off:** Timescale's continuous aggregates are free to self-host, but AWS RDS / Aurora and Cloud SQL
  don't offer them. On those, the fallback is a rollup table updated on insert, or moving analytics to
  ClickHouse.

### No foreign keys on `calls`

On a 100M-row hypertable, foreign keys slow down every insert. The API is the only writer and validates
the account (API key) and the campaign (tracking number) on the way in.

### Idempotent ingestion

Telephony webhooks retry. `external_id` (the provider's call id) has a partial unique index
`(account_id, external_id, started_at)`, and the insert uses `ON CONFLICT DO NOTHING`. A retry returns
`200` with the stored call and is not re-published. Timescale requires the time column in every unique
index; a genuine retry carries the same `started_at`, so that's fine. A retry with a *different*
`started_at` would be stored twice — a known limitation.

Calls older than 3 days are rejected with `422`: they'd fall outside the aggregate's refresh window and
never show up in the charts. Old data goes through the backfill path.

### Real-time: SSE + Redis pub/sub

The dashboard only receives, so Server-Sent Events fit better than WebSockets: plain HTTP, automatic
reconnect, nothing to send back. Each API process holds **one** Redis subscription and fans events out to
its own browsers through in-memory queues. A browser that falls 100 events behind is disconnected instead of
growing memory; `EventSource` reconnects on its own and the UI reloads the feed. A heartbeat comment every
15 seconds keeps proxies from closing idle connections.

### Auth: people log in, machines use keys

- **Users:** email + password (bcrypt) → JWT in an **httpOnly cookie**. A cookie and not an
  `Authorization` header because the browser's `EventSource` can't send custom headers. httpOnly keeps the
  token away from JavaScript (XSS); `SameSite=Lax` blocks cross-site POSTs (CSRF).
- **Simulator:** an API key per account in the `X-API-Key` header.

### Filters

Date range, campaigns and outcomes apply to the volume chart and the feed. The **conversion rate ignores
the outcome filter**: a conversion rate over only missed calls is always 0% and means nothing. The UI says
so under the chart. Live calls are filtered in the browser, so changing a filter doesn't reopen the stream.

## Code organization

See [conventions.md](conventions.md). Backend layers: routers (thin) → actions (business logic) →
repositories (one query each). Explanations live in this file, not in code comments.
