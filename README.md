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

The application is for historical research and education. It does not execute trades, connect to a broker, or provide investment advice.