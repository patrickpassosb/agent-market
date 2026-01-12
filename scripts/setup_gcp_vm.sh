#!/usr/bin/env bash
set -euo pipefail

# Bootstraps the repository on a GCP VM after it is created (installs deps, deploys via Docker).
echo ">>> Starting GCP VM setup..."

REPO_DIR="${REPO_DIR:-$HOME/agent-market}"
REPO_URL="${REPO_URL:-}"

if ! command -v git >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y git
fi

if [ ! -d "$REPO_DIR/.git" ]; then
  if [ -z "$REPO_URL" ]; then
    echo "REPO_URL is required when the repo is not present."
    echo "Example: REPO_URL=https://github.com/<owner>/<repo> bash scripts/setup_gcp_vm.sh"
    exit 1
  fi
  git clone "$REPO_URL" "$REPO_DIR"
fi

if ! command -v curl >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y curl
fi

bash "$REPO_DIR/scripts/setup_ec2.sh"

if [ ! -f "$REPO_DIR/.env" ]; then
  if [ -n "${ENV_FILE_B64:-}" ]; then
    (umask 077 && echo "$ENV_FILE_B64" | base64 -d > "$REPO_DIR/.env")
  elif [ -n "${ENV_FILE_PATH:-}" ] && [ -f "$ENV_FILE_PATH" ]; then
    (umask 077 && cp "$ENV_FILE_PATH" "$REPO_DIR/.env")
  fi
fi

if [ ! -f "$REPO_DIR/.env" ]; then
  echo ">>> .env still missing. Set ENV_FILE_B64 or copy your .env into $REPO_DIR before deploy."
  exit 1
fi

echo ">>> Deploying app..."
if ! sudo bash "$REPO_DIR/scripts/deploy.sh"; then
  echo ">>> Deployment failed. If .env was missing, update it and rerun:"
  echo "    sudo bash $REPO_DIR/scripts/deploy.sh"
  exit 1
fi

echo ">>> Setup complete. Verify the app via the VM external IP."
