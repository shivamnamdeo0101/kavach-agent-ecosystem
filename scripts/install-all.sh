#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGES=(
  "kavach-logger"
  "kavach-mcp-events"
  "kavach-shield"
  "kavach-mcp-gateway"
)

for pkg in "${PACKAGES[@]}"; do
  pip install -e "${ROOT_DIR}/${pkg}"
done

pip install fastapi
echo "All packages installed!"
