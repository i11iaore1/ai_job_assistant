#!/bin/sh

set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 $@