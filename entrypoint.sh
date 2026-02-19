#!/bin/sh

echo "Waiting for database..."

until pg_isready -h $DB_HOST -p $DB_PORT -U $POSTGRES_USER
do
  sleep 2
done

echo "Database is ready!"

echo "Running setup_db..."
python -m app.setup_db

echo "Creating super admin..."
flask create-default-admin || true

echo "Starting Flask..."
exec flask run --host=0.0.0.0 --port=5000
