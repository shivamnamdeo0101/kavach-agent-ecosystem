#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGES=(
  "kavach-logger"
  "kavach-mcp-events"
  "kavach-shield"
  "kavach-mcp-gateway"
)

python -m pip install --upgrade build twine

for pkg in "${PACKAGES[@]}"; do
  echo "Building ${pkg}..."
  cd "${ROOT_DIR}/${pkg}"
  rm -rf dist build *.egg-info
  python -m build
  twine upload --skip-existing --verbose dist/*
done

echo "All packages deployed to PyPI!"
