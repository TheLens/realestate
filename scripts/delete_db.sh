#!/bin/bash

# Setup database
echo "Force users to quit realestate database session..."
psql realestate -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE datname = current_database()
AND pid <> pg_backend_pid();"

echo "Backing up database..."
pg_dump realestate > $BACKUP_DIR/db-$(date +%Y-%m-%d-%H-%M-%S).sql

echo "Drop citysalaries database if it exists..."
dropdb --if-exists realestate

# os.environ.get('REAL_ESTATE_DATABASE_USERNAME'),
# os.environ.get('REAL_ESTATE_DATABASE_PASSWORD'),
