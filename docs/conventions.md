# Code Conventions

The goal is code someone else can read without help. These rules apply to the backend, the simulator
and the frontend.

## Readability

1. **No comments in application code.** No inline comments, block comments or docstrings. If code needs
   a comment, rename or extract until it doesn't. The *why* behind design decisions lives in
   [architecture.md](architecture.md). Config files (`docker-compose.yml`, `nginx.conf`, `config.py`)
   are the exception.
2. **Small functions.** A function or method is at most 20 lines. Extract well-named private helpers.
   Alembic migrations are exempt: an `upgrade()` that creates tables reads best as one list of steps.
3. **No abbreviations, no placeholder names.** `call_filter`, not `f`; `bucket`, not `b`;
   `timezone`, not `tz`. If a variable holds a value used once, inline it.
4. **Named constants, not magic numbers.** `MAX_HOURLY_RANGE = timedelta(days=31)`, never a bare `31`.
5. **Lines break only past 120 characters.**
6. **English only.**

## Backend layers

| Layer | Folder | Role |
|---|---|---|
| Router | `app/routers/` | Thin: resolve dependencies, call one action or repository method, return. No business logic. |
| Dependency | `app/dependencies/` | Who is calling (JWT cookie or API key) and request filters. The tenant always comes from here, never from the URL. |
| Action | `app/actions/` | Business logic orchestration. A class: inputs go through `__init__`, `__call__` takes no arguments. |
| Repository | `app/repositories/` | One method = one query. No branching between queries, no business rules. |
| Schema | `app/schemas/` | Request and response shapes (Pydantic). Separate from the database models. |
| Model | `app/models/` | SQLAlchemy models, one per file. Enums carry their own helper methods. |
| Service | `app/services/` | External systems only (Redis pub/sub). |

## Tests

1. `pytest`, integration tests against a real PostgreSQL — never mocks for SQL.
2. Each endpoint's test file is ordered: authentication → validation → happy path.
3. Requests go through helpers in `tests/helpers.py` (`send_volume_request(...)`), not raw client calls.
4. Pin every attribute an assertion depends on; never rely on random fixture data.
