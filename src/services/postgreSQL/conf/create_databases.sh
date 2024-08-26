#!/bin/bash
set -e

# Wait for PostgreSQL to start
until psql -U "$POSTGRES_USER" -c '\q' > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL to be available..."
    sleep 2
done

# Create databases
createdb -U "$POSTGRES_USER" users
# createdb -U "$POSTGRES_USER" game_history
createdb -U "$POSTGRES_USER" authentication
createdb -U "$POSTGRES_USER" games