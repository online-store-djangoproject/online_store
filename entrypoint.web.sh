#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time
import psycopg2

if os.getenv("DB_ENGINE", "sqlite") == "sqlite":
    raise SystemExit(0)

for attempt in range(60):
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "5432"),
        )
        conn.close()
        print("PostgreSQL is ready.")
        break
    except Exception as exc:
        if attempt == 59:
            raise
        print(f"PostgreSQL is not ready yet: {exc}")
        time.sleep(2)
PY

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting web server..."
exec "$@"
