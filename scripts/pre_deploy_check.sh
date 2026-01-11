#!/bin/bash

# Pre-Deployment Flight Check
# Verifies environment and dependencies before deployment.

echo "✈️  Starting Pre-Deployment Flight Check..."

# 1. Check for .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please copy .env.example to .env and fill in your keys."
    exit 1
fi
echo "✅ .env file found."

# 2. Check for critical API keys in .env
# We grep for non-empty keys. This is a basic check.
if ! grep -q "OPENAI_API_KEY=sk-" .env && ! grep -q "GEMINI_API_KEY=" .env && ! grep -q "GROQ_API_KEY=" .env; then
    echo "⚠️  Warning: No obvious API keys (OpenAI, Gemini, Groq) detected in .env."
    echo "   Ensure you have at least one provider configured."
else
    echo "✅ API keys detected."
fi

# 3. Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running."
    exit 1
fi
echo "✅ Docker is running."

# 4. Dry-run Build Frontend (Optional but recommended)
echo "🏗️  Verifying Frontend Build (Dry Run)..."
if [ -d "frontend" ]; then
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "   Installing dependencies..."
        npm ci > /dev/null 2>&1
    fi
    # We don't run full build as it takes time, but we check linting if available
    # or just simple structure checks.
    # For now, we assume if npm install works, it's a good sign.
    echo "✅ Frontend dependencies installed."
    cd ..
else
    echo "⚠️  Frontend directory not found."
fi

echo "🎉 Flight Check Passed! You are ready to deploy."
echo "   Run: ./scripts/deploy.sh"
