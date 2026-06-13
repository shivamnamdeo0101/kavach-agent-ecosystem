#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🧹 Cleaning up build artifacts..."

# Cleanup kavach-logger
echo "Cleaning kavach-logger..."
cd kavach-logger
rm -rf dist build *.egg-info
cd ..

# Cleanup kavach-mcp-events
echo "Cleaning kavach-mcp-events..."
cd kavach-mcp-events
rm -rf dist build *.egg-info
cd ..

# Cleanup kavach-shield
echo "Cleaning kavach-shield..."
cd kavach-shield
rm -rf dist build *.egg-info
cd ..

echo "✅ Cleanup complete!"