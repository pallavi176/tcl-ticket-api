# TCL Ticket API

Production-style **FastAPI** service for the TCL interview assignment: create, read, and update ticket rows in MySQL database **TestDB**, table **tblTicketDetails**, with **async SQLAlchemy 2.x**, **Pydantic v2**, layered architecture (repositories + services), structured logging, JWT auth, and **rate limiting** (SlowAPI / in-memory; swap for Redis in multi-node deployments).

## Purpose

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tickets` | Create a ticket |
| `GET` | `/tickets` | List tickets (paginated: `skip`, `limit`) |
| `GET` | `/tickets/{id}` | Get ticket details |
| `PUT` | `/tickets/{id}` | Update ticket (partial update) |
| `PATCH` | `/tickets/{id}` | Same as PUT — change one or more fields |
| `POST` | `/tickets/{id}/close` | Set status to `closed` |

Supporting routes:

- `POST /auth/token` — OAuth2 password form; returns JWT for `Authorization: Bearer …` (demo user from env).
- `GET /health` — liveness probe (no auth).

Interactive docs: `GET /docs` (Swagger UI), `GET /redoc`.

## Repository layout

```
app/
  api/v1/          # Routers (HTTP)
  core/            # Exceptions, security (JWT), limiter, middleware hooks, decorators
  db/              # Async engine + session dependency
  models/          # SQLAlchemy ORM
  repositories/    # Data access
  schemas/         # Pydantic models
  services/        # Use-cases / business rules
  middleware/      # Request ID propagation
sql/
  ddl.sql          # MySQL DDL (assignment + indexes)
  queries_reference.sql  # Equivalent SQL (documentation)
nginx/
  nginx.conf       # Reverse proxy sample
postman/
  TCL-Ticket-API.postman_collection.json
tests/             # pytest + httpx AsyncClient (SQLite in-memory)
```

## Prerequisites

- Python **3.11+**
- **MySQL 8+** (local or Docker) when not running tests (tests use SQLite via dependency override).
- **Docker Desktop** (or Docker Engine + Compose v2) if you use the Compose workflow below.

## Project setup

From the machine where you cloned the repo:

1. **Enter the project directory**

   ```bash
   cd ticket-api
   ```

2. **Create local environment file**

   ```bash
   cp .env.example .env          # Linux / macOS (Git Bash)
   copy .env.example .env        # Windows CMD
   ```

   Edit `.env`: set a strong `JWT_SECRET_KEY` (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`). Match `DATABASE_URL` to how you run MySQL (see **Docker Compose** host ports below if the DB runs in Compose).

3. **Choose one runtime**

   - **Docker (MySQL + API):** see [Docker Compose](#docker-compose-mysql--api--nginx). No host Python or local MySQL required for the API container.
   - **Python on the host:** create a venv, install deps, run MySQL (Compose or local install), then uvicorn — see [Local run (uvicorn)](#local-run-uvicorn).

4. **Optional — checks before deploy or sharing artifacts**

   ```bash
   pip install -e ".[dev]"       # if not already installed
   black app tests
   flake8 app tests
   pylint app
   pytest tests -v --cov=app --cov-report=term-missing
   ```

## Configuration

Copy `.env.example` to `.env` in the project root (same folder as `pyproject.toml`). Full comments and examples are in **`.env.example`**.

| Variable | Meaning |
|----------|---------|
| `APP_NAME` | OpenAPI title. Quote if it contains spaces, e.g. `"TCL Ticket API"`. |
| `DEBUG` | `true` enables SQL echo and more verbose behavior (dev only). |
| `DATABASE_URL` | Async SQLAlchemy URL, e.g. `mysql+asyncmy://user:pass@127.0.0.1:3306/TestDB`. URL-encode special characters in user/password. If MySQL runs in Docker Compose and the host maps **3307→3306**, use `127.0.0.1:3307` when the **app runs on the host** (uvicorn). |
| `JWT_SECRET_KEY` | Secret for signing JWTs (use a long random value in production). |
| `JWT_ALGORITHM` | Default `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifetime of tokens from `POST /auth/token`. |
| `DEMO_USERNAME` / `DEMO_PASSWORD` | Demo user for `/auth/token` only. |
| `ENABLE_AUTH` | `true` = JWT required on `/tickets*`. `false` = local smoke tests only. |
| `CORS_ORIGINS` | JSON array, e.g. `["*"]` or `["http://localhost:3000"]`. Comma-separated URLs are also accepted. |
| `LOG_LEVEL` | One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `LOG_JSON` | `true` / `false` for log line format. |
| `RATE_LIMIT_DEFAULT` | SlowAPI limit for `POST`/`PUT` `/tickets`, e.g. `60/minute`. |
| `RATE_LIMIT_BURST` | SlowAPI limit for `GET` `/tickets/{id}`, e.g. `120/minute`. |

## Database setup

1. Run the DDL script (creates database, table, indexes):

   ```bash
   mysql -u root -p < sql/ddl.sql
   ```

2. Or use Docker Compose (see below), which mounts `sql/ddl.sql` into MySQL init.

Logical SQL equivalents of ORM operations are documented in `sql/queries_reference.sql`. The app does **not** use stored procedures; all access is through SQLAlchemy.

## Local run (uvicorn)

```bash
cd ticket-api
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e ".[dev]"
```

Ensure MySQL is up and `DATABASE_URL` points at **TestDB**. Then:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Compose (MySQL + API + nginx)

All commands below are run from the **`ticket-api`** directory (where `docker-compose.yml` lives).

### Common commands

| Task | Command (bash / Git Bash) | Windows PowerShell |
|------|---------------------------|---------------------|
| Build all images | `docker compose build` | same |
| Start DB + API only (no nginx) | `docker compose up -d db api` | same |
| Start full stack (includes nginx on port 80) | `docker compose up -d` | same |
| Rebuild **api** after code changes | `docker compose build api && docker compose up -d api` | `docker compose build api; docker compose up -d api` |
| Clean rebuild **api** (no cache) | `docker compose build --no-cache api && docker compose up -d api` | `docker compose build --no-cache api; docker compose up -d api` |
| Follow API logs | `docker compose logs -f api` | same |
| Stop containers and default network | `docker compose down` | same |

### Published ports (host)

The values in **`docker-compose.yml`** may use alternate host ports if **3306** or **8000** are already in use on your machine. Check the `ports:` mappings there; defaults in this repo are:

| Service | Host URL / connection | Inside Compose network |
|---------|------------------------|---------------------------|
| **API** | `http://127.0.0.1:8001` → container `8000` | `http://api:8000` |
| **MySQL** | `127.0.0.1:3307` (user `app`, password `appsecret`, DB `TestDB`) → container `3306` | host name `db`, port `3306` |
| **nginx** (if `docker compose up -d`) | `http://localhost:80` | proxies to `api:8000` |

To use standard **8000** / **3306** on the host, edit `docker-compose.yml` `ports:` to `8000:8000` and `3306:3306` when those ports are free.

### JWT secret with Compose

Compose substitutes `JWT_SECRET_KEY` from your project **`.env`** for the `api` service. You can also pass it for one run:

- **bash:** `JWT_SECRET_KEY=your_hex_secret docker compose up -d`
- **PowerShell:** `$env:JWT_SECRET_KEY='your_hex_secret'; docker compose up -d`

## Railway (public URL)

The Docker image listens on **`PORT`** (Railway sets this). If you see Railway’s “train has not arrived at the station” page:

1. **Redeploy** after pulling the latest `Dockerfile` (must use `${PORT:-8000}` in the `uvicorn` command).
2. **`tcl-ticket-api` service → Settings → Networking** — enable **Public networking** and **Generate domain** (or attach the domain you expect).
3. **`tcl-ticket-api` → Deployments** — confirm the latest deploy is **Active** (not crashed). Open **View logs** if the status is failed: fix `DATABASE_URL`, missing env vars, or build errors.
4. **`tcl-ticket-api` → Variables** — set `DATABASE_URL` to internal MySQL (e.g. host `mysql.railway.internal`, database `TestDB` after running `sql/ddl.sql`).

Then open `https://<your-domain>/health` — expect `{"status":"ok"}`.

## Authentication

1. `POST /auth/token` with form fields `username` and `password` (`application/x-www-form-urlencoded`).
2. Use returned `access_token` as `Authorization: Bearer <token>` on ticket routes.

With `ENABLE_AUTH=false`, ticket routes accept requests without a bearer token (development convenience only).

## Rate limiting

SlowAPI is configured with per-route limits (e.g. create/update **60/minute**, read **120/minute**, keyed by client IP). On limit you receive **429** (SlowAPI default body). For horizontally scaled APIs, replace the in-memory limiter storage with Redis-backed limits.

## Error model

JSON envelope (non-success):

```json
{
  "success": false,
  "error": {
    "code": "TICKET_NOT_FOUND",
    "message": "Ticket 99999 not found",
    "field": null
  },
  "request_id": "…",
  "details": null
}
```

Typical status codes: **400** (business validation), **401** (auth), **404** (missing ticket), **422** (request body validation), **429** (rate limit), **500** (unexpected).

## Curl examples (for screenshots)

Replace `TOKEN` after calling `/auth/token`. Replace `BASE` with your API base URL (e.g. `http://127.0.0.1:8001` when using the Compose host port from this repo’s `docker-compose.yml`).

```bash
BASE=http://127.0.0.1:8001

# Token
curl -s -X POST "$BASE/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo"

# Create
curl -s -X POST "$BASE/tickets" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Sample\",\"description\":\"Desc\",\"status\":\"open\",\"priority\":\"MEDIUM\",\"assigned_to\":\"bob\"}"

# List
curl -s "$BASE/tickets?skip=0&limit=50" -H "Authorization: Bearer TOKEN"

# Get
curl -s "$BASE/tickets/1" -H "Authorization: Bearer TOKEN"

# Update (or PATCH with the same JSON body for partial changes)
curl -s -X PUT "$BASE/tickets/1" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"closed\",\"priority\":\"LOW\"}"

# Close (shortcut for status closed)
curl -s -X POST "$BASE/tickets/1/close" -H "Authorization: Bearer TOKEN"
```

Postman: import `postman/TCL-Ticket-API.postman_collection.json`, run **Auth — obtain JWT**, copy `access_token` into collection variable `token`, then invoke the ticket requests.

## Quality tooling

```bash
black app tests
flake8 app tests
pylint app
pytest tests -v --cov=app --cov-report=term-missing
```

Configuration: `pyproject.toml` (Black, pytest), `.flake8` (Flake8).

## Design notes (scalability)

- **Async I/O** end-to-end for DB drivers suitable for MySQL under load.
- **Stateless API** behind nginx; scale API containers independently.
- **JWT** for authentication; **opaque API keys** or OAuth2 delegation would replace demo credentials in production.
- **Repository + service** layers keep SQL and business rules testable and swappable.
- **Decorators** (`log_execution`, `translate_db_errors`) centralize cross-cutting persistence concerns.
- **Request ID** middleware supports log correlation across proxies (`X-Request-ID`).

## License

Provided for the TCL interview submission.
