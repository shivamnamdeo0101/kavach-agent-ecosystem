#!/bin/bash
cd kavach-logger && pip install -e . && cd ..
cd kavach-mcp-events && pip install -e . && cd ..
cd kavach-shield && pip install -e . && cd ..
pip install fastapi
echo "✅ All packages installed!"
