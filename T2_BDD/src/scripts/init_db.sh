#!/bin/bash
# Initialize the database schema
# Usage: ./T2_BDD/src/scripts/init_db.sh

# Database connection parameters (can be overridden by environment variables)

# Ensure we are in the project root
if [ ! -d "T2_BDD" ]; then
    echo "Error: Please run this script from the project root (SAE5-C-IDFou)."
    exit 1
fi

# Load environment variables from .env if present
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Database connection parameters
DB_NAME=${DB_NAME:-sae5idfou}
DB_USER=${DB_USER:-idfou}
# Ensure DB_ROOT_PASSWORD is available
if [ -z "$DB_ROOT_PASSWORD" ]; then
    echo "Warning: DB_ROOT_PASSWORD is not set. You might be prompted for a password."
fi

echo "Initializing database '$DB_NAME' with user '$DB_USER'..."

# Check if container is running
if [ -z "$(docker ps -q -f name=sae5db)" ]; then
    echo "Error: Container 'sae5db' is not running. Please start it with 'docker-compose up -d'."
    exit 1
fi

docker exec -e PGPASSWORD="${DB_ROOT_PASSWORD}" -w /app sae5db psql -U "$DB_USER" -d "$DB_NAME" -f T2_BDD/src/sql/schema.sql

if [ $? -eq 0 ]; then
    echo "Schema initialized successfully."
else
    echo "Error initializing schema."
    exit 1
fi
