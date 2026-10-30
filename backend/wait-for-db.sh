#!/bin/sh
set -e

HOST="${POSTGRES_HOST:-postgres}"
PORT="${POSTGRES_PORT:-5432}"
USER="${POSTGRES_USER:-postgres}"

echo "Waiting for PostgreSQL at $HOST:$PORT..."

until pg_isready -h "$HOST" -p "$PORT" -U "$USER" > /dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL is ready!"
