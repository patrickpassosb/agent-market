#!/usr/bin/env bash
set -euo pipefail

echo ">>> Deploying Agent Market..."

# 1. Pull latest code (if in a git repo)
if [ -d .git ]; then
    echo ">>> Pulling latest changes from git..."
    git pull origin main
fi

# 2. Check for .env file
if [ ! -f .env ]; then
    echo "!!! WARNING: .env file missing. Creating from example..."
    cp .env.example .env
    echo "!!! Please edit .env with your real API keys before continuing."
    exit 1
fi

# 3. Build and restart services
echo ">>> Building and starting containers..."
docker compose -f docker-compose.prod.yml up -d --build

# 4. Cleanup old images
echo ">>> Cleaning up old images..."
docker image prune -f

echo ">>> Deployment Successful!"
echo ">>> Check logs with: docker compose -f docker-compose.prod.yml logs -f"
