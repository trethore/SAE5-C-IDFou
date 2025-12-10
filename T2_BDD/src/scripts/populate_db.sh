#!/bin/bash
# Populate the database with data
# Usage: ./T2_BDD/src/scripts/populate_db.sh

# Database connection parameters

# Ensure we are in the project root to find CSV files
if [ ! -d "T1_analyse_de_donnees" ]; then
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

if [ -z "$DB_ROOT_PASSWORD" ]; then
    echo "Warning: DB_ROOT_PASSWORD is not set. You might be prompted for a password."
fi

echo "Populating database '$DB_NAME'..."

# Check if container is running
if [ -z "$(docker ps -q -f name=sae5db)" ]; then
    echo "Error: Container 'sae5db' is not running. Please start it with 'docker-compose up -d'."
    exit 1
fi

docker exec -e PGPASSWORD="${DB_ROOT_PASSWORD}" -w /app sae5db psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f T2_BDD/src/sql/populate.sql

if [ $? -eq 0 ]; then
    echo "Database populated successfully."
else
    echo "Error populating database."
    exit 1
fi
