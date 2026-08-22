# Trade Track

Trade Track is a lightweight, mobile-first trading journal PWA. It supports isolated multi-user journals, multiple trading accounts, manual trade CRUD, filtering, calculated balances, and server-derived performance analytics. The frontend is a statically deployable SvelteKit PWA; the backend is a Render-ready FastAPI modular monolith backed by Neon PostgreSQL.

## Architecture

Backend requests flow through `router → service → repository → SQLAlchemy → PostgreSQL`. Routers stay HTTP-focused, services own business and authorization rules, and repositories own persistence. Future imports use `BrokerAdapter → SyncService → TradeService`, ensuring external trades pass through the same validation as manual trades. No broker is implemented in V1.

The frontend uses one authenticated SvelteKit layout, a centralized API client, reusable feature components, and a fixed shared bottom navigation. Statistics are calculated once by the backend rather than duplicated in UI components.

## Stack and structure

- `backend/`: Python, FastAPI, async SQLAlchemy 2, Pydantic 2, Alembic, PostgreSQL, JWT, Argon2
- `frontend/`: SvelteKit 5, TypeScript, Tailwind CSS 4, Chart.js, vite-plugin-pwa, static adapter
- `render.yaml`: backend deployment blueprint

## Local setup

Prerequisites: Python 3.12+, Node 20+, and PostgreSQL (or a Neon connection string).

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Set `DATABASE_URL` to an async SQLAlchemy URL. For Neon this commonly resembles `postgresql+asyncpg://USER:PASSWORD@HOST/DB?ssl=require`. Set a long random `JWT_SECRET_KEY`; configure comma-separated `ALLOWED_ORIGINS` such as `http://localhost:5173,https://your-frontend.example`. API docs are at `/docs`; health is at `/health`.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Set `PUBLIC_API_URL=http://localhost:8000/api/v1`. Only public backend location data belongs here—never database credentials or JWT secrets.

## Database and migrations

Create a Neon project, copy its connection values into `backend/.env`, then run `alembic upgrade head`. Production schema management uses Alembic, not `create_all`. Generate future migrations from `backend/` with `alembic revision --autogenerate -m "description"`, review them, then upgrade.

## Testing and production builds

```powershell
cd backend
pytest

cd ..\frontend
npm run check
npm run build
npm run preview
```

Tests use a separate in-memory SQLite database and cover registration/login, invalid credentials, account ownership, trade ownership/listing, derived stats, balances, and protected deletion. The frontend build emits static assets to `frontend/build`; deploy that directory on any static host and route unknown paths to `index.html`.

## PWA

The Vite PWA integration produces the manifest and service worker, caches static assets, and uses standalone display mode. `static/icon.svg` is a functional placeholder; replace it with production 192px and 512px PNG assets when branding is finalized. V1 intentionally does not attempt offline trade synchronization.

## Render deployment

Create a service from `render.yaml` or use its commands manually. Set `DATABASE_URL`, `JWT_SECRET_KEY`, and the exact frontend origin in `ALLOWED_ORIGINS`. The start command applies migrations before starting Uvicorn. After deployment, set the static host's `PUBLIC_API_URL` to `https://YOUR-API/api/v1` and rebuild the frontend.

## API summary

- Auth: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- Accounts: authenticated CRUD at `/api/v1/accounts`
- Trades: authenticated CRUD at `/api/v1/trades`, with account/side/symbol/asset/search filters and pagination
- Stats: `GET /api/v1/stats/overview?range=7d|1m|3m|all`
- Calendar: `GET /api/v1/calendar?year=YYYY&month=M` and `GET /api/v1/calendar/{date}`

Every account and trade query is scoped to the JWT-derived user. The API never accepts a user ID for authorization.
