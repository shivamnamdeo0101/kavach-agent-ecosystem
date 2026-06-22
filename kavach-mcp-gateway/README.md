# Kavach MCP Gateway

Config-driven API gateway for Model Context Protocol (MCP) with dynamic routing via YAML configuration.

Integrates with other Kavach packages for logging, events, and optional security scanning.

## Features

- **Config-driven routing**: Define all routes in a single YAML file
- **No code changes for new services**: Add routes by editing `routes.yaml`
- **Path prefix matching**: Routes requests based on path prefixes
- **MCP tool routing**: Route tool calls to the right MCP server by tool name
- **Minimal overhead**: Lightweight and performant routing logic
- **Kavach integration**:
  - Structured logging via `kavach-logger` with optional data masking
  - Event emission via `kavach-events` for route changes and matches
  - Optional security scanning via `kavach-shield` (install with `[security]` extra)

## Installation

```bash
pip install kavach-mcp-gateway
```

With optional security support:

```bash
pip install kavach-mcp-gateway[security]
```

## Quick Start

### 1. Create routes configuration in your project

Create `routes.yaml` in your application directory:

```yaml
routes:
  - prefix: /auth
    target: http://localhost:8001
  - prefix: /users
    target: http://localhost:8002
  - prefix: /orders
    target: http://localhost:8003
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
```

### 2. Use in your application

```python
from kavach_gateway import MCPGateway

gateway = MCPGateway()
gateway.load_routes("routes.yaml")

# Get target for a request path
target = gateway.get_target("/auth/login")
# Returns: "http://localhost:8001"

# Get target for an MCP tool call
target = gateway.get_tool_target("weather.forecast")
# Returns: "http://localhost:9001"

# Check all configured routes
routes = gateway.get_routes()
# Returns: ['/auth', '/users', '/orders', '/mcp/weather']

# Check all configured MCP tools
tools = gateway.get_tools()
# Returns: ['github.create_issue', 'github.list_repos', 'weather.current', 'weather.forecast', ...]

# Reload routes (useful for hot-reloading)
gateway.reload()
```

## API Reference

### MCPGateway

**Methods:**

- `load_routes(config_path)` - Load routes from YAML configuration file
- `get_target(path)` - Get target URL for a request path
- `get_tool_target(tool_name)` - Get target URL for an MCP tool name
- `match(path)` - Get RouteConfig object for a path
- `match_tool(tool_name)` - Get RouteConfig object for a tool name
- `get_routes()` - Get list of all configured route prefixes
- `get_tools()` - Get list of all configured MCP tool names
- `reload()` - Reload routes from last loaded configuration file

**Events emitted** (via `kavach-events`):

- `gateway_routes_loaded` - When routes are successfully loaded
- `gateway_route_matched` - When a request path matches a route
- `gateway_tool_matched` - When an MCP tool name matches a route
- `gateway_load_error` - When route loading fails
- `gateway_reload_started` - When route reloading begins

### SecurityScanner

Optional security scanning for requests (requires `kavach-shield`):

```python
from kavach_gateway import SecurityScanner

scanner = SecurityScanner(enabled=True)
violations = scanner.scan_path("/auth/login")
```

**Methods:**

- `scan_path(path)` - Scan request path for violations
- `scan_body(body)` - Scan request body for violations

## Integration with Other Kavach Packages

### Logging

The gateway uses `kavach-logger` for structured logging with optional data masking:

```python
from kavach_gateway import MCPGateway
from kavach_logger import get_logger

logger = get_logger("my.gateway", masked=True)
gateway = MCPGateway()
gateway.load_routes("routes.yaml")
```

### Events

Subscribe to gateway events using `kavach-events`:

```python
from kavach_events import event_manager

@event_manager.subscribe(["gateway_route_matched"])
async def on_route_matched(payload):
    print(f"Route matched: {payload['path']} -> {payload['target']}")

gateway.load_routes("routes.yaml")  # Triggers event
```

### Security Scanning

Optional security scanning using `kavach-shield`:

```bash
pip install kavach-mcp-gateway[security]
```

```python
from kavach_gateway import SecurityScanner

scanner = SecurityScanner(enabled=True)
violations = scanner.scan_path("/auth/login")
if violations:
    print(f"Security violations found: {len(violations)}")
```

## License

MIT
