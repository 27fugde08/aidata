#!/bin/bash

# Ensure script stops on error
set -e

echo "🚀 Starting AIOS Enterprise System..."

# Check if .env exists, if not create from example or warn
if [ ! -f .env ]; then
    echo "⚠️ .env file not found! Please create one."
    exit 1
fi

echo "📦 Building and Starting Docker Containers..."
docker-compose up -d --build

echo "⏳ Waiting for Database to be ready..."
# Simple wait loop (could be improved with pg_isready)
sleep 10

echo "🔄 Running Database Migrations..."
docker-compose exec backend alembic upgrade head

echo "✅ AIOS System is Running!"
echo "👉 Backend API: http://localhost:8000/docs"
echo "👉 Frontend App: http://localhost:3000"
