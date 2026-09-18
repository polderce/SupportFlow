#!/bin/sh

set -e

echo "Применяем миграции базы данных..."
python manage.py migrate --noinput

exec "$@"

