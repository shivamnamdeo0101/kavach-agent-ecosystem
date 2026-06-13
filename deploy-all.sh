#!/bin/bash
echo "Building kavach-logger..."
cd kavach-logger && python -m build && twine upload dist/* && cd ..

echo "Building kavach-mcp-events..."
cd kavach-mcp-events && python -m build && twine upload dist/* && cd ..

echo "Building kavach-shield..."
cd kavach-shield && python -m build && twine upload dist/* && cd ..

echo "✅ All packages deployed to PyPI!"
