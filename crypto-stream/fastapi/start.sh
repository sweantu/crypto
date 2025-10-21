#!/bin/bash
set -e  # exit immediately on error

# --- Wait for Postgres to be ready ---
echo "⏳ Waiting for Postgres..."
until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done
echo "✅ Postgres is up!"

# --- Run migrations ---
echo "🚀 Running Alembic migrations..."
alembic upgrade head

# --- Start FastAPI app ---
echo "🏁 Starting FastAPI..."
exec python run.py