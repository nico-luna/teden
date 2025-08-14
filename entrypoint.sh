#!/usr/bin/env bash
set -euo pipefail

# Defaults
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-core.settings}
export PORT=${PORT:-8000}
export DB_HOST=${DB_HOST:-db}
export DB_PORT=${DB_PORT:-5432}
export DB_USER=${DB_USER:-postgres}
export DB_NAME=${DB_NAME:-postgres}

# Esperar a Postgres (requiere postgresql-client en la imagen)
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
  echo "⏳ Esperando PostgreSQL en ${DB_HOST}:${DB_PORT}..."
  sleep 1
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Levantar el server
exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers ${WEB_CONCURRENCY:-3} \
  --timeout 120