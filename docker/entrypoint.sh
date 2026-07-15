#!/bin/sh
set -e

echo "DB_HOST=$DB_HOST, DB_USER=$DB_USER, DB_NAME=$DB_NAME"

echo "Waiting for database..."
until nc -z "$DB_HOST" "${DB_PORT:-3306}"; do
  echo "Database unavailable - sleeping 2s"
  sleep 2
done
echo "Database is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting application..."
exec gunicorn flow.wsgi:application --bind 0.0.0.0:8000 --workers 3
