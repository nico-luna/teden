#!/bin/sh

echo "Esperando que la base de datos esté lista..."
while ! nc -z db 5432; do
  sleep 0.1
done

echo "Base de datos lista. Corriendo migraciones..."
python manage.py migrate

echo "Levantando el servidor..."
exec python manage.py runserver 0.0.0.0:8000