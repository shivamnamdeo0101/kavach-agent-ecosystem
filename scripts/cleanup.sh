#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🧹 Cleaning up build artifacts and cache..."

# Cleanup kavach-logger
echo "Cleaning kavach-logger..."
cd kavach-logger
rm -rf dist build *.egg-info __pycache__ .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
cd ..

# Cleanup kavach-mcp-events
echo "Cleaning kavach-mcp-events..."
cd kavach-mcp-events
rm -rf dist build *.egg-info __pycache__ .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
cd ..

# Cleanup kavach-shield
echo "Cleaning kavach-shield..."
cd kavach-shield
rm -rf dist build *.egg-info __pycache__ .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
cd ..

# Cleanup root level
echo "Cleaning root level..."
rm -rf __pycache__ .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

echo "✅ Cleanup complete!"