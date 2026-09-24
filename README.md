# AlgoResearch

AlgoResearch is a reproducible historical market-research workspace. It brings market classification, technical screening, strategy evaluation, data-quality checks, and research-run reporting into one workflow.

This project is designed for research and education. It does not execute orders, connect to a broker, or provide investment advice.

## What It Does

- Classifies recent OHLC structure as bullish, bearish, or sideways.
- Calculates candle partition values and supporting market evidence.
- Screens the NIFTY universe using EMA 20/50 crossover rules.
- Uses Yahoo Finance when enabled and local historical fixtures in offline mode.
- Analyzes uploaded trade CSV files with P&L, win rate, profit factor, equity, and drawdown metrics.
- Runs permutation Monte Carlo analysis on trade sequences.
- Validates OHLC CSV files before analysis.
- Stores research runs in SQLite with parameters, timestamps, sources, and summaries.
- Provides a React workspace for dashboards, screening, backtests, comparisons, and run history.

## Architecture

```text
React + Vite frontend
				|
				| HTTP / JSON
				v
Flask API
	|-- analytics       classification, indicators, crossover, P&L, Monte Carlo
	|-- providers       Yahoo Finance, local CSV, uploaded CSV
	|-- validation      OHLC, request, and upload validation
	|-- services         market, scanner, backtest, and workspace orchestration
	|-- store            SQLite research-run persistence
	v
Historical fixtures and uploaded research data
```

## Quick Start

### 1. Install dependencies

```bash
make setup
```

The command creates a Python virtual environment, installs backend dependencies, and installs frontend dependencies from `package-lock.json`.

### 2. Start the backend

In terminal one:

```bash
make backend
```

The API runs at `http://127.0.0.1:5001`.

### 3. Start the frontend

In terminal two:

```bash
make frontend
```

Open `http://127.0.0.1:5173` in your browser and select **Open workspace**.

The default local run uses included historical fixtures and does not require API keys or network access.

## Development Commands

Run the complete local quality gate:

```bash
make check
```

Individual commands:

```bash
# Backend tests
source .venv/bin/activate
pytest -q

# Frontend checks
cd frontend
npm run lint
npm run build
```

GitHub Actions runs the backend tests and frontend checks on pushes and pull requests through `.github/workflows/ci.yml`.

## Configuration

Copy the example configuration before running the backend:

```bash
cp .env.example .env
```

Important settings:

| Setting | Purpose | Local default |
| --- | --- | --- |
| `ALGORESEARCH_OFFLINE` | Disable remote market-data requests | `false` |
| `HOST` | Backend bind address | `127.0.0.1` |
| `PORT` | Backend port | `5001` |
| `CORS_ORIGINS` | Allowed frontend origins | Local Vite URLs |
| `MAX_UPLOAD_MB` | Maximum CSV upload size | `5` |
| `AUTH_ENABLED` | Enable session authentication | `false` |

For a secure deployment, set `AUTH_ENABLED=1`, a long random `SECRET_KEY`, and non-default `AUTH_USERNAME` and `AUTH_PASSWORD`. The server rejects enabled authentication when its secret or password is missing or left at a known default.

## Main API Routes

| Route | Purpose |
| --- | --- |
| `GET /api/health` | Service health check |
| `GET /api/dashboard` | Dashboard summary and latest runs |
| `POST /api/market/classify` | Classify a market using a configured provider |
| `POST /api/market/classify-csv` | Classify uploaded OHLC data |
| `POST /api/scanner/run` | Run EMA crossover screening |
| `GET /api/scanner/symbol/<symbol>` | Inspect one symbol |
| `POST /api/backtest/analyze-csv` | Analyze uploaded trades |
| `POST /api/backtest/monte-carlo` | Run trade-sequence Monte Carlo analysis |
| `POST /api/backtest/compare` | Compare built-in research datasets |
| `POST /api/data-quality/validate-csv` | Validate uploaded OHLC data |
| `GET /api/research-runs` | List saved research runs |
| `POST /api/auth/login` | Start an authenticated session |

## Repository Layout

```text
backend/       Flask API and research services
data/          Historical fixtures and sample datasets
frontend/      React/Vite user interface
tests/         Backend regression and security tests
Makefile       Setup, run, test, and build shortcuts
render.yaml    Optional Render deployment definition
```

## Security and Reliability

- Local dataset path traversal and symlink escapes are blocked.
- Request symbols and numeric parameters are validated and bounded.
- Upload size, extension, row count, and CSV structure are checked.
- Public API errors do not expose internal exception details.
- Authentication uses Flask sessions and constant-time credential comparison.
- Security response headers are applied by the Flask app.
- Runtime SQLite state, uploads, caches, and secrets are excluded from Git.

## Data and Interpretation Notes

Results depend on the quality, period, and source of the historical data. Screening output identifies research candidates; it is not a buy or sell instruction. Backtest and Monte Carlo results describe historical inputs and assumptions, not guaranteed future performance.

## Deployment

`render.yaml` defines a Flask API and static Vite frontend. Before deploying, replace the example service URLs in `CORS_ORIGINS` and `VITE_API_URL`, configure a strong authentication secret if needed, and choose persistent storage appropriate for the deployment environment. SQLite is suitable for the local demo; a managed database is preferable for multi-user production use.

## Contributing

1. Create a feature branch.
2. Make a focused change with regression coverage.
3. Run `make check`.
4. Open a pull request describing the behavior, tests, and any data assumptions.