#!/bin/bash
# OBCMS Docker Development Startup Script

set -euo pipefail

echo "🐳 Starting OBCMS Docker Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update if needed."
fi

# Build and start services
echo "🔨 Building Docker images..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until docker compose exec -T db pg_isready -U obcms > /dev/null 2>&1; do
    echo "   Database not ready yet, retrying in 2s..."
    sleep 2
done
echo "✅ Database is ready!"

# Run migrations
echo "🔄 Running database migrations..."
docker compose exec web python src/manage.py migrate

echo "✅ OBCMS is ready!"
echo ""
echo "🌐 Access the application:"
echo "   - Web: http://localhost:8000"
echo "   - Admin: http://localhost:8000/admin/"
echo ""
echo "📊 Service status:"
docker compose ps
echo ""
echo "📝 To create a superuser:"
echo "   docker compose exec web python src/manage.py createsuperuser"
echo ""
echo "🔍 To view logs:"
echo "   docker compose logs -f"
