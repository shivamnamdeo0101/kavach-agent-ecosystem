#!/bin/bash
cd kavach-logger && pip install -e . && cd ..
cd kavach-mcp-events && pip install -e . && cd ..
cd kavach-shield && pip install -e . && cd ..
echo "✅ All packages installed!"
