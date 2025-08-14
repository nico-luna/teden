#!/bin/sh
set -eu

# Defaults
: "${DJANGO_SETTINGS_MODULE:=teden.settings}"
: "${PORT:=8000}"
: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"
: "${DB_USER:=postgres}"

echo "⏳ Esperando PostgreSQL en ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" >/dev/null 2>&1; do
  sleep 1
done
echo "✅ PostgreSQL OK"

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

echo "🚀 Gunicorn en 0.0.0.0:${PORT}"
exec gunicorn teden.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-3}" \
  --timeout 120

