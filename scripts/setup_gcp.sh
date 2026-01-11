#!/usr/bin/env bash
set -euo pipefail

# Context7 docs:
# - https://github.com/googlecloudplatform/python-docs-samples/blob/main/endpoints/getting-started-grpc/README.md
# - https://cloud.google.com/sdk/gcloud/reference/index
# Fallback docs (Context7 command detail unavailable):
# - https://docs.cloud.google.com/sdk/gcloud/reference/compute/firewall-rules/create
# No API version constraints mentioned in the referenced docs.

usage() {
  cat <<'USAGE'
Usage:
  PROJECT_ID=<your-project-id> [INSTANCE_NAME=agent-market] ./scripts/setup_gcp.sh

Optional env:
  ZONE=<zone> (e.g., southamerica-east1-c)
  IMAGE_FAMILY=debian-12
  IMAGE_PROJECT=debian-cloud
  NETWORK=default
  HTTP_TAG=http-server
  HTTPS_TAG=https-server
  INSTANCE_TAGS=http-server,https-server
  SOURCE_RANGES=0.0.0.0/0
  FIREWALL_HTTP_RULE=allow-http-agent-market
  FIREWALL_HTTPS_RULE=allow-https-agent-market
  ALLOW_HTTP=1
  ALLOW_HTTPS=1
  ENV_FILE_PATH=<path-to-env>
  ENV_FILE_B64=<base64-encoded-env>
  AUTO_PROVISION=1  (create VM, set firewall rules, and run remote setup)
  AUTO_SSH=1        (auto-run gcloud compute ssh after creation)
USAGE
}

require_env() {
  local name="$1"
  if [ -z "${!name:-}" ]; then
    echo "Missing required env: $name"
    usage
    exit 1
  fi
}

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI not found. Install Google Cloud SDK and retry."
  exit 1
fi

require_env PROJECT_ID

INSTANCE_NAME="${INSTANCE_NAME:-agent-market}"
IMAGE_FAMILY="${IMAGE_FAMILY:-debian-12}"
IMAGE_PROJECT="${IMAGE_PROJECT:-debian-cloud}"
NETWORK="${NETWORK:-default}"
HTTP_TAG="${HTTP_TAG:-http-server}"
HTTPS_TAG="${HTTPS_TAG:-https-server}"
INSTANCE_TAGS="${INSTANCE_TAGS:-${HTTP_TAG},${HTTPS_TAG}}"
SOURCE_RANGES="${SOURCE_RANGES:-0.0.0.0/0}"
FIREWALL_HTTP_RULE="${FIREWALL_HTTP_RULE:-allow-http-agent-market}"
FIREWALL_HTTPS_RULE="${FIREWALL_HTTPS_RULE:-allow-https-agent-market}"
ALLOW_HTTP="${ALLOW_HTTP:-1}"
ALLOW_HTTPS="${ALLOW_HTTPS:-1}"
AUTO_PROVISION="${AUTO_PROVISION:-0}"
AUTO_SSH="${AUTO_SSH:-0}"
ZONE="${ZONE:-}"

REPO_URL="${REPO_URL:-}"
if [ -z "$REPO_URL" ]; then
  REPO_URL="$(git config --get remote.origin.url 2>/dev/null || true)"
fi

normalize_repo_url() {
  local url="$1"
  if [[ "$url" == git@github.com:* ]]; then
    url="https://github.com/${url#git@github.com:}"
  fi
  echo "${url%.git}"
}

if [ -n "$REPO_URL" ]; then
  REPO_URL="$(normalize_repo_url "$REPO_URL")"
fi

ENV_FILE_PATH="${ENV_FILE_PATH:-}"
ENV_FILE_B64="${ENV_FILE_B64:-}"
if [ -z "$ENV_FILE_B64" ] && [ -n "$ENV_FILE_PATH" ]; then
  if [ ! -f "$ENV_FILE_PATH" ]; then
    echo "ENV_FILE_PATH does not exist: $ENV_FILE_PATH"
    exit 1
  fi
  ENV_FILE_B64="$(base64 < "$ENV_FILE_PATH" | tr -d '\n')"
fi

ZONE_FLAG=()
if [ -n "$ZONE" ]; then
  ZONE_FLAG+=(--zone "$ZONE")
fi

MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-4}"

echo ">>> Enabling Compute Engine API for project: $PROJECT_ID"
gcloud services enable compute.googleapis.com --project "$PROJECT_ID"

ensure_firewall_rule() {
  local name="$1"
  local port="$2"
  local tags="$3"

  if gcloud compute firewall-rules list \
    --project "$PROJECT_ID" \
    --format="value(name)" \
    | grep -qx "$name"; then
    echo ">>> Firewall rule exists: $name"
    return
  fi

  echo ">>> Creating firewall rule: $name (tcp:$port)"
  gcloud compute firewall-rules create "$name" \
    --project "$PROJECT_ID" \
    --network "$NETWORK" \
    --direction=INGRESS \
    --allow="tcp:$port" \
    --source-ranges="$SOURCE_RANGES" \
    --target-tags="$tags"
}

if [ "$ALLOW_HTTP" = "1" ]; then
  ensure_firewall_rule "$FIREWALL_HTTP_RULE" "80" "$HTTP_TAG"
fi

if [ "$ALLOW_HTTPS" = "1" ]; then
  ensure_firewall_rule "$FIREWALL_HTTPS_RULE" "443" "$HTTPS_TAG"
fi

echo ">>> Creating Compute Engine instance: $INSTANCE_NAME ($MACHINE_TYPE)"
gcloud compute instances create "$INSTANCE_NAME" \
  --project "$PROJECT_ID" \
  --machine-type "$MACHINE_TYPE" \
  --image-family "$IMAGE_FAMILY" \
  --image-project "$IMAGE_PROJECT" \
  --tags "$INSTANCE_TAGS" \
  "${ZONE_FLAG[@]}"

echo ">>> Instance created."
if [ "$AUTO_PROVISION" = "1" ]; then
  if [ -z "$REPO_URL" ]; then
    echo "AUTO_PROVISION requires REPO_URL to be set (or a git remote)."
    exit 1
  fi

  REMOTE_CMD=$(cat <<EOF
set -euo pipefail
if ! command -v git >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y git
fi
if [ ! -d "\$HOME/agent-market/.git" ]; then
  git clone "$REPO_URL" "\$HOME/agent-market"
fi
cd "\$HOME/agent-market"
REPO_URL="$REPO_URL" ENV_FILE_B64="$ENV_FILE_B64" bash scripts/setup_gcp_vm.sh
EOF
)

  echo ">>> Running remote VM bootstrap and deploy..."
  gcloud compute ssh "$INSTANCE_NAME" \
    --project "$PROJECT_ID" \
    "${ZONE_FLAG[@]}" \
    --command "$REMOTE_CMD"
else
  echo ">>> Next steps (run on your machine):"
  echo "  gcloud compute ssh $INSTANCE_NAME --project $PROJECT_ID ${ZONE_FLAG[*]}"
  echo ">>> On the VM, run:"
  if [ -n "$REPO_URL" ]; then
    echo "  git clone $REPO_URL agent-market"
  else
    echo "  git clone <your-repo-url> agent-market"
  fi
  echo "  cd agent-market"
  if [ -n "$ENV_FILE_B64" ]; then
    echo "  ENV_FILE_B64='<base64>' bash scripts/setup_gcp_vm.sh"
  else
    echo "  REPO_URL=${REPO_URL:-<your-repo-url>} bash scripts/setup_gcp_vm.sh"
  fi
fi

if [ "$AUTO_SSH" = "1" ]; then
  gcloud compute ssh "$INSTANCE_NAME" --project "$PROJECT_ID" "${ZONE_FLAG[@]}"
fi
