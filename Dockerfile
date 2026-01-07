# Base Image: Python 3.12 Slim
# We use the slim variant to reduce image size while maintaining necessary build tools.
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# System Dependencies
# 'build-essential' is often required for compiling Python extensions (e.g., ChromaDB's dependencies).
# We clean up the apt cache afterwards to keep the layer small.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dependency Management: uv
# We use 'uv' for extremely fast dependency resolution and installation.
RUN pip install uv

# 1. Copy dependency definitions first (caching layer)
# This allows Docker to cache the installed dependencies if pyproject.toml/uv.lock haven't changed.
COPY pyproject.toml uv.lock ./

# 2. Install dependencies
# --frozen: strict adherence to the lockfile.
# --no-install-project: we only want libraries, not the app itself installed as a package.
RUN uv sync --frozen --no-install-project

# 3. Copy Application Code
# This changes most frequently, so it's placed last.
COPY . .

# Runtime Command
# We use 'uv run' to execute the script within the managed virtual environment context.
CMD ["uv", "run", "main.py"]