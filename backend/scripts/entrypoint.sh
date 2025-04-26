#!/bin/bash

set -e  # Stop on error

# Configure environment
export PYTHONPATH=/app
LOG_PREFIX="[PD-APP-BACKEND]"

echo "$LOG_PREFIX Initializing application..."

# Check for Azure deployment
if [ "$AZURE_DEPLOYMENT" = "true" ]; then
    echo "$LOG_PREFIX Running in Azure environment"
    
    # Set up connection parameters from environment variables
    export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
    echo "$LOG_PREFIX Database connection configured for Azure PostgreSQL"
    
    # Wait for max 5 minutes (30 * 10 seconds) for database to be ready
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    echo "$LOG_PREFIX Waiting for Azure Database to be ready..."
    until PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -q; do
        RETRY_COUNT=$((RETRY_COUNT+1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "$LOG_PREFIX Failed to connect to database after $MAX_RETRIES attempts, exiting"
            exit 1
        fi
        echo "$LOG_PREFIX Azure Database not ready (attempt $RETRY_COUNT/$MAX_RETRIES), retrying in 10 seconds..."
        sleep 10
    done
    echo "$LOG_PREFIX Azure Database is ready!"
else
    echo "$LOG_PREFIX Running in local development environment"
    
    echo "$LOG_PREFIX Waiting for Database to be ready..."
    until PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
        echo "$LOG_PREFIX Database not ready, retrying in 3 seconds..."
        sleep 3
    done
    echo "$LOG_PREFIX Database is ready!"
fi

# Apply database schema and data
if [ -f "/app/pd_management.sql" ] && [ "$AZURE_DEPLOYMENT" != "true" ]; then
    echo "$LOG_PREFIX Restoring Database from SQL Dump File..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "/app/pd_management.sql" || echo "$LOG_PREFIX SQL restore failed."
    echo "$LOG_PREFIX Database restoration complete!"
else
    echo "$LOG_PREFIX Running database migrations..."
    alembic upgrade head || { echo "$LOG_PREFIX Migrations failed, check logs!"; exit 1; }
    echo "$LOG_PREFIX Migrations completed successfully."

    if [ "$RUN_SEEDER" = "true" ]; then
        echo "$LOG_PREFIX Running Seeder Script..."
        python scripts/seeder.py || echo "$LOG_PREFIX Seeder failed, continuing..."
    else
        echo "$LOG_PREFIX Seeder Skipped (Set RUN_SEEDER=true to enable)"
    fi
fi

# Wait for HAPI FHIR server if specified and not running in Azure
if [ -n "$HAPI_BASE_URL" ] && [ "$AZURE_DEPLOYMENT" != "true" ]; then
    echo "$LOG_PREFIX Waiting for HAPI FHIR server to be available..."
    MAX_RETRIES=10
    RETRY_COUNT=0
    
    until curl --silent --output /dev/null --fail "$HAPI_BASE_URL" || [ $RETRY_COUNT -ge $MAX_RETRIES ]; do
        RETRY_COUNT=$((RETRY_COUNT+1))
        echo "$LOG_PREFIX HAPI FHIR server not ready, waiting... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 3
    done
    
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "$LOG_PREFIX HAPI FHIR server is ready!"
    else
        echo "$LOG_PREFIX HAPI FHIR server not available after $MAX_RETRIES attempts, continuing anyway..."
    fi
fi

# Run sample patient initialization
if [ "$LOAD_SAMPLE_PATIENTS" = "true" ]; then
    echo "$LOG_PREFIX Running sample patient record initialization..."
    python scripts/seed_sample_patients.py || echo "$LOG_PREFIX Sample patient seeder failed, continuing..."
else
    echo "$LOG_PREFIX Sample patient initialization skipped"
fi

# Start the application
echo "$LOG_PREFIX Starting FastAPI application server..."

# Determine log level and reload settings based on environment
if [ "$AZURE_DEPLOYMENT" = "true" ]; then
    # Production settings - no reload, configured log level
    LOG_LEVEL=${LOG_LEVEL:-"info"}
    exec uvicorn app.api.main:app --host 0.0.0.0 --port 8004 --log-level $LOG_LEVEL
else
    # Development settings - with reload, debug logging
    exec uvicorn app.api.main:app --host 0.0.0.0 --port 8004 --reload --log-level debug
fi
