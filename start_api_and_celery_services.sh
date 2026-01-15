#!/usr/bin/env bash
set -euo pipefail

echo "Running migrations..."
alembic upgrade head

echo "Starting API + Celery worker + Celery beat..."

uvicorn app.main:app --host 0.0.0.0 --port 8000 &

celery -A worker.celery_app:get_celery_app worker --loglevel=INFO &

celery -A worker.celery_app:get_celery_app beat --loglevel=INFO &

wait -n
