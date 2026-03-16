#!/bin/bash
# AIHRT – Database migration setup script

set -e

echo "🔷 AIHRT Database Setup"
echo "========================"

# Initialize alembic
cd backend
alembic init migrations

# Generate initial migration
alembic revision --autogenerate -m "initial_schema"

# Run migration
alembic upgrade head

echo "✅ Database migrations complete"
