#!/bin/bash
set -e

echo "Starting Celery worker..."
exec celery -A src worker --loglevel=info
