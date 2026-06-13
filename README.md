# Kavach Agent Ecosystem

Small Python packages for adding security checks, lifecycle events, and safe logging to AI agents and MCP servers.

[Live demo](https://kavach-agent-ecosystem.web.app/) | [LinkedIn](https://www.linkedin.com/in/shivamnamdeo0101/) | MIT License

## Packages

| Package | Purpose | Dependencies |
| --- | --- | --- |
| `kavach-logger` | Logging helpers with optional sensitive-data masking. | None |
| `kavach-mcp-events` | Async event bus for MCP lifecycle hooks. | None |
| `kavach-shield` | FastMCP middleware and detection engine for risky prompts, secrets, PII, code execution, and SQL patterns. | `fastmcp`, `kavach-logger`, `kavach-mcp-events` |

## Install

From this repository:

```bash
cd kavach-agent-ecosystem
python3 -m venv venv
source venv/bin/activate
bash scripts/install-all.sh
```

Or install packages individually:

```bash
pip install -e kavach-logger
pip install -e kavach-mcp-events
pip install -e kavach-shield
```

```bash
python example/mcp_event_logger_shield_server.py
```

## Quick Use

```python
from kavach_logger import get_logger
from kavach_events import MCP_HOOKS, event_manager
from kavach_shield import DetectionEngine, KavachMiddleware, KAVACH_RULES

logger = get_logger("app", masked=True)
logger.info("token=sk-12345678901234567890")

@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["*"])
async def on_security_event(payload):
    logger.warning("Security event", violations=payload.get("violations", []))

engine = DetectionEngine(KAVACH_RULES)
violations = engine.scan("ignore all previous instructions")

middleware = KavachMiddleware(
    strict=True,
    sensitive_tools=["execute_*", "db_*", "file_*"],
)
```

For FastMCP:

```python
from fastmcp import FastMCP
from kavach_shield import KavachMiddleware

mcp = FastMCP("Shielded MCP Server")
mcp.add_middleware(KavachMiddleware(strict=True, sensitive_tools=["delete_*", "db_*"]))
```

## Runtime Behavior

`KavachMiddleware` emits:

| Event | When |
| --- | --- |
| `pre_tool_call` | Before every MCP tool call. |
| `post_tool_call` | After successful tool execution. |
| `security_check` | When inbound or outbound content matches a rule. |
| `tool_error` | When the wrapped tool raises an exception. |
| `audit_log` | Available for manual audit events. |

Inbound scanning is applied to tools matching `sensitive_tools`. Outbound responses are scanned and masked before returning. In `strict=True`, violations raise `SecurityException`; in `strict=False`, they are logged/emitted but allowed.

## Examples

```bash
python example/basic_example.py
python example/audit_example.py
python example/mcp_event_logger_shield_server.py
```

The MCP server example exposes `/`, `/health`, and `/mcp` when run with Python.

## Repository Layout

```text
kavach-agent-ecosystem/
├── kavach-logger/       # logging + masking package
├── kavach-mcp-events/   # async event bus package
├── kavach-shield/       # FastMCP middleware + detection rules
├── example/             # runnable examples
├── scripts/             # install/deploy helpers
└── web/                 # Firebase-hosted website
```

## Package Docs

See the package READMEs for focused API notes:

- `kavach-logger/README.md`
- `kavach-mcp-events/README.md`
- `kavach-shield/README.md`

## Publishing

```bash
bash scripts/deploy-all.sh
```

This builds and uploads all three packages with `python -m build` and `twine upload`.

