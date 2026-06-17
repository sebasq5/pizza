#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "from sqlalchemy import create_engine; from sqlalchemy import text; import os; engine=create_engine(os.environ['DATABASE_URL']); conn=engine.connect(); conn.execute(text('SELECT 1')); conn.close()" >/dev/null 2>&1
do
  sleep 2
done

# flask db upgrade

flask seed

exec gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 run:app
