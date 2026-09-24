.PHONY: setup backend frontend test check

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r backend/requirements.txt
	cd frontend && npm install

backend:
	. .venv/bin/activate && ALGORESEARCH_OFFLINE=1 FLASK_DEBUG=0 python backend/run.py

frontend:
	cd frontend && npm run dev -- --host 127.0.0.1

test:
	. .venv/bin/activate && pytest -q

check: test
	cd frontend && npm run lint && npm run build