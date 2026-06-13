# Kavach Shield

Security middleware and detection engine for FastMCP servers.

## Install

```bash
pip install kavach-shield
```

For local development:

```bash
pip install -e .
```

`kavach-shield` depends on `fastmcp`, `kavach-logger`, and `kavach-mcp-events`.

## Built-In Rules

`KAVACH_RULES` includes regex rules for:

- Prompt injection.
- Data exfiltration.
- PII-like numbers.
- Secret/API key leakage.
- Dangerous `eval`/`exec`/subprocess patterns.
- SQL injection patterns.

Each rule is a `Rule(id, name, severity, description, patterns)` dataclass.

## Detection Engine

```python
from kavach_shield import DetectionEngine, KAVACH_RULES

engine = DetectionEngine(KAVACH_RULES)
violations = engine.scan("ignore all previous instructions")

for violation in violations:
    print(violation["rule"], violation["severity"])
```

`scan(text)` returns dictionaries with `rule`, `name`, and `severity`.

## FastMCP Middleware

```python
from fastmcp import FastMCP
from kavach_shield import KavachMiddleware

mcp = FastMCP("Shielded Server")

shield = KavachMiddleware(
    strict=True,
    sensitive_tools=["execute_*", "db_*", "delete_*"],
)

mcp.add_middleware(shield)
```

Middleware behavior:

- Emits `pre_tool_call` before every tool call.
- Scans inbound arguments only for tools matching `sensitive_tools`.
- Scans outbound responses for all tools.
- Emits `security_check` when rules match.
- Emits `tool_error` when a wrapped tool raises.
- Emits `post_tool_call` after successful execution.
- Masks sensitive strings in string responses and FastMCP text content.

In `strict=True`, violations raise `SecurityException`. In `strict=False`, violations are logged and emitted without blocking.

## Custom Rules

```python
import re
from kavach_shield import KavachMiddleware, Rule

custom_rules = [
    Rule(
        id="command-injection",
        name="Command Injection",
        severity="high",
        description="Shell command separators and risky binaries",
        patterns=[
            re.compile(r"(;|&&|\|\||`|\$\()", re.I),
            re.compile(r"\b(rm|curl|wget|bash|sh)\b", re.I),
        ],
    )
]

shield = KavachMiddleware(
    rules=custom_rules,
    extend_rules=True,  # default: append custom rules to KAVACH_RULES
    strict=True,
)
```

Set `extend_rules=False` to use only the rules you pass.

## Sensitive Tools

Sensitive tools support shell-style wildcards via `fnmatch`:

```python
shield = KavachMiddleware(sensitive_tools=["db_*", "file_write", "execute_*"])
shield.register_tool("admin_delete_user")
```

## Events

```python
from kavach_events import MCP_HOOKS, event_manager

@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["*"])
async def log_security(payload):
    print(payload["tool_name"], payload.get("violations", []))
```

Event payloads include `tool_name`, `arguments`, `context`, `is_sensitive`, and event-specific fields such as `violations`, `stage`, `response`, or `error`.

## Static Processing

For non-MCP payloads:

```python
from kavach_shield import KavachMiddleware

shield = KavachMiddleware(strict=True)
result = shield.process({"tool": "db_query", "query": "select 1"})
```

Returns `{"allowed": True, "data": ...}` or raises `SecurityException` in strict mode.

