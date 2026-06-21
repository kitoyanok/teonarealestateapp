#!/bin/sh
set -eu

PYTHON_SEARCH_PORT="${PYTHON_SEARCH_PORT:-8002}"
PORT="${PORT:-10000}"

python3 -m uvicorn app.main:app \
  --app-dir /app/apps/search-service \
  --host 127.0.0.1 \
  --port "${PYTHON_SEARCH_PORT}" &

exec env \
  NODE_ENV=production \
  PORT="${PORT}" \
  SEARCH_SERVICE_URL="${SEARCH_SERVICE_URL:-http://127.0.0.1:${PYTHON_SEARCH_PORT}}" \
  npm run start --workspace @estateflow/api
