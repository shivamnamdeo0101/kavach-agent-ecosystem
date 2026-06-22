#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGES=(
  "kavach-logger"
  "kavach-mcp-events"
  "kavach-shield"
  "kavach-mcp-gateway"
)

echo "Cleaning build artifacts and caches..."

for pkg in "${PACKAGES[@]}"; do
  echo "Cleaning ${pkg}..."
  cd "${ROOT_DIR}/${pkg}"
  rm -rf dist build *.egg-info __pycache__ .pytest_cache
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
  find . -type f -name "*.pyc" -delete
done

echo "Cleaning root level..."
cd "${ROOT_DIR}"
rm -rf __pycache__ .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

echo "Cleanup complete!"
