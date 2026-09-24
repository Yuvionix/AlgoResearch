# AlgoResearch

AlgoResearch is a historical market-research workspace. It combines OHLC market classification, EMA 20/50 screening, backtest analytics, Monte Carlo trade-sequence analysis, CSV data-quality checks, and saved research runs.

## Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
pytest -q
python backend/run.py
```

The API runs at `http://127.0.0.1:5001`. Set `ALGORESEARCH_OFFLINE=1` in `.env` to use only the included historical fixtures.

## One-command checks

After setup, use the root `Makefile` targets:

```bash
make setup
make check
```

Run the two local services in separate terminals with `make backend` and `make frontend`, then open `http://127.0.0.1:5173`.

## Deployment

`render.yaml` defines a deployment-ready Flask API and static Vite frontend. Connect this repository to Render, review the generated service URLs, update `CORS_ORIGINS` and `VITE_API_URL` with those URLs, and deploy. The included manifest keeps the demo offline and does not require market-data credentials.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite app runs at `http://127.0.0.1:5173`.

## Checks

```bash
cd frontend
npm run lint
npm run build
```

GitHub Actions runs the same backend tests and frontend lint/build checks on pushes and pull requests through `.github/workflows/ci.yml`.

The application is for historical research and education. It does not execute trades, connect to a broker, or provide investment advice.

Authentication is available for deployments by setting `AUTH_ENABLED=1`, a strong `SECRET_KEY`, and non-default `AUTH_USERNAME` and `AUTH_PASSWORD`. The server rejects enabled authentication when the secret or password is missing/default, and the frontend provides login/logout controls. Authentication remains disabled by default so the included offline demo opens immediately.

Research runs are stored in SQLite at `data/research_runs.sqlite3` and are ignored by Git because they are local runtime state.