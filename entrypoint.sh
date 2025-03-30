#!/bin/bash

# Function to check if MySQL is up and running
function mysql_ready() {
    uvx python << END
import sys
import mysql.connector
try:
    mysql.connector.connect(
        user="${MYSQL_USER}",
        password="${MYSQL_PASSWORD}",
        host="${MYSQL_HOST}",
        database="${MYSQL_DATABASE}",
        port=${MYSQL_PORT:-3306}
    )
except Exception as e:
    print(e)
    sys.exit(1)
sys.exit(0)
END
}

# Wait for MySQL to be ready
until mysql_ready; do
    echo "Waiting for MySQL to be ready..."
    sleep 2
done

echo "MySQL is ready! Starting Flask application..."

# Initialize database if not already initialized
if [ ! -f "/app/.db_initialized" ]; then
    echo "Initializing database..."
    uvx flask db init
    uvx flask db migrate -m "Initial migration"
    uvx flask db upgrade
    touch /app/.db_initialized
    echo "Database initialized!"
else
    echo "Database already initialized, running migrations if needed..."
    uvx flask db migrate -m "Auto migration"
    uvx flask db upgrade
fi

# Execute the CMD from the Dockerfile
# exec "$@"
