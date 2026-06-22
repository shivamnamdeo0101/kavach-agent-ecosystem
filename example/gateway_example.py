"""Small example for kavach-mcp-gateway path and MCP tool routing."""
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kavach-mcp-gateway"))
sys.path.insert(0, str(ROOT / "kavach-logger"))
sys.path.insert(0, str(ROOT / "kavach-mcp-events"))

from kavach_gateway import MCPGateway


ROUTES_YAML = """
routes:
  - prefix: /mcp/weather
    target: http://localhost:9001
    name: weather
    tools:
      - current
      - forecast

  - prefix: /mcp/github
    target: http://localhost:9002
    name: github
    tools:
      - create_issue
      - list_repos
"""


def main():
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as routes_file:
        routes_file.write(ROUTES_YAML)
        routes_path = routes_file.name

    gateway = MCPGateway()
    gateway.load_routes(routes_path)

    print("Path route:")
    print("/mcp/weather/call ->", gateway.get_target("/mcp/weather/call"))

    print("\nTool routes:")
    print("weather.forecast ->", gateway.get_tool_target("weather.forecast"))
    print("github.create_issue ->", gateway.get_tool_target("github.create_issue"))

    print("\nAvailable tools:")
    for tool in gateway.get_tools():
        print("-", tool)


if __name__ == "__main__":
    main()
