#!/bin/bash

set -e  # Stop on error

echo " Waiting for Database to be ready..."
until PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo " Database not ready, retrying in 3 seconds..."
  sleep 3
done
echo " Database is ready!"

if [ -f "/app/pd_management.sql" ]; then
  echo " Restoring Database from SQL Dump File..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "/app/pd_management.sql" || echo " SQL restore failed."
  echo " Database restoration complete!"
else
  echo " No SQL Dump File Found, Running Migrations Instead..."
  alembic upgrade head || echo " Migrations failed, check logs!"

  if [ "$RUN_SEEDER" = "true" ]; then
    echo " Running Seeder Script..."
    python scripts/seeder.py || echo " Seeder failed, continuing..."
  else
    echo " Seeder Skipped (Set RUN_SEEDER=true to enable)"
  fi
fi

echo " Running sample patient record init..."
# adds all sample patient data for testing alerts/notifications
python scripts/seed_sample_patients.py || echo " sample patient seeder failed, continuing..."

echo " Starting FastAPI server..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8004 --reload --log-level debug
