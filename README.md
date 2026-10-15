# Call Analytics Dashboard

A real-time dashboard for a marketing manager: call volume (hourly and daily), conversion rate by campaign and by
source, a live feed of calls, and filters for date range, campaign and outcome.

![Dashboard](docs/dashboard.png)

## Run it

Needs only Docker.

```bash
docker compose up --build
```

Open http://localhost:1011 and click one of the demo accounts:

| Company | Email | Password |
|---|---|---|
| Acme Home Services (Chicago) | `manager@acme.test` | `acme-demo` |
| Summit Auto Group (New York) | `manager@summit.test` | `summit-demo` |

The first start creates the database and seeds 500,000 calls per company over the last 90 days (about 10 seconds,
~240 MB). A simulator then sends new calls, and the page updates every 10 seconds.

The default is small on purpose: the design is built for much more data, but 50 million calls per company take about
20 GB of disk, and I didn't want to fill your machine without asking. The larger run is one command away (below).

- API docs: http://localhost:1012/docs
- Faster simulator: `CALLS_PER_SECOND=2 docker compose up` (`0` pauses it)
- Ports taken? `WEB_PORT=1021 API_PORT=1022 docker compose up`
- Start over: `docker compose down -v`

## Tests

```bash
docker compose --profile test run --rm api-tests   # backend: 99 tests against a real PostgreSQL
cd frontend && npm install && npm test              # frontend: 75 tests
```

## 50 million calls per company

```bash
docker compose down -v
SEED_CALLS_PER_ACCOUNT=50000000 docker compose up --build
```

About 10 minutes of seeding and 20 GB of disk. Measured on a Mac Studio (M2 Max; Docker Desktop with 8 CPUs and 16 GB), one company,
median of 5 runs:

| Query | Counting raw calls | Reading the hourly counters |
|---|---:|---:|
| Hourly volume, last 7 days | 1,510 ms | 0.7 ms |
| Daily volume, last 90 days | 21,811 ms | 4.6 ms |
| Conversion by campaign, last 30 days | 1,178 ms | 0.7 ms |

Every dashboard request answers in under 10 ms end to end. Rerun it with
`docker compose run --rm setup python -m scripts.benchmark`.

## Decision summary

### What I built

A dashboard that shows a marketing manager how their inbound calls are doing: call volume (hourly and daily), conversion rate by campaign and by source, a live feed of calls, and filters for date range, campaign and outcome. The page refreshes every 10 seconds.

- **Backend:** FastAPI on plain PostgreSQL 17, the same engine as AWS RDS.
- **Frontend:** Vue 3 + Chart.js, served by nginx.
- **Simulator:** posts calls to the API the way a telephony provider's webhook would.
- **Live updates:** Redis passes each new call to every API process, and each one pushes it to its open dashboards over Server-Sent Events.
- **Two demo companies** share the same tables; each one only sees its own data.

### Key trade-offs

- **Plain Postgres, so it runs on AWS RDS.** Calls are split into daily partitions, and an hourly counters table keeps the charts fast at 100M calls. The cost: keeping the counters right is our code's job, not the database's. Without the RDS requirement, TimescaleDB would do both out of the box.
- **Refresh every 10 seconds instead of on every call.** A new call can take up to 10 seconds to appear, but the database load no longer grows with call volume: a busy company with 20 dashboards open sends 2 queries per second instead of one per call per dashboard.
- **One shared database for all companies, with `account_id` on every row.** Cheap to run, and every query only reads one company's slice. The cost: a very large customer shares the database with everyone else, so at scale the biggest ones would move to their own shard.

### What I'd do with more time

- Show calls while they're still ringing (today a call appears when it ends).
- Update the charts straight from the live calls the browser already receives, instead of asking the API every 10 seconds, so the numbers move as soon as a call comes in.
- Browser end-to-end tests and a load test on the live stream.

### Intentionally left out

- Signup, password reset and roles.
- HTTPS (a load balancer's job).
- Editing campaigns.

### Assumptions

- A call has one outcome: missed, connected (answered, no sale) or converted (led to a sale or booking).
- Conversion rate = converted ÷ all calls. The outcome filter doesn't change it.
- Each campaign has its own tracking number; that's how a call is tied to a campaign.
- Days follow the company's timezone.

### How I used AI

I used AI (Claude Code) for the whole process. We brainstormed approaches together, and I made the calls on stack, data model, multi-tenancy, the real-time approach and scope. From the brief we built a checklist of requirements and tests and worked through it item by item. The AI wrote all of the code, following my coding and testing standards ([docs/conventions.md](docs/conventions.md)) and the functionality and usability we defined. At the end I also used it to review the codebase, fix what it found, improve test coverage and challenge our decisions, and to write the documentation and the architecture diagram.

Where I relied on AI the most was the performance strategy: daily partitions plus an hourly counters table. We discussed several options, and I asked questions until I understood the trade-offs, but in the end I followed its recommendation. The right strategy depends on the shape of the data, not only its size. I'm comfortable extending it, for example adding a new dimension to the counters or dropping old partitions.


## More detail

- [docs/architecture.md](docs/architecture.md): how it works and why
- [docs/architecture.png](docs/architecture.png): the diagram
- [docs/conventions.md](docs/conventions.md): code conventions

## Project layout

```
docker-compose.yml   db, redis, setup, api, simulator, frontend (+ api-tests profile)
backend/             FastAPI app, migrations, seed, tests, benchmark
simulator/           sends fake calls to the API like a telephony provider
frontend/            Vue 3 app, tests, nginx config
docs/                architecture, diagram, conventions
```
