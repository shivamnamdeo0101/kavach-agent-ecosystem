# Kavach MCP Events

Zero-dependency async event bus for MCP lifecycle hooks.

## Install

```bash
pip install kavach-mcp-events
```

For local development:

```bash
pip install -e .
```

## Hooks

`MCP_HOOKS` defines the standard event names used by `kavach-shield`:

| Hook | Meaning |
| --- | --- |
| `PRE_TOOL_CALL` | Before a tool runs. |
| `POST_TOOL_CALL` | After a tool succeeds. |
| `SECURITY_CHECK` | A security rule matched. |
| `TOOL_ERROR` | Tool execution failed. |
| `AUDIT_LOG` | Manual audit event. |

## Quick Use

```python
from kavach_events import MCP_HOOKS, event_manager

@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL], tools=["*"])
async def before_any_tool(payload):
    print(payload["tool_name"])

@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["db_query"])
def on_db_security_event(payload):
    print(payload.get("violations", []))

await event_manager.emit(
    MCP_HOOKS.SECURITY_CHECK,
    "db_query",
    {"violations": [{"rule": "sql-injection"}]},
)
```

Sync callbacks are run in an executor. Async callbacks are awaited concurrently. Listener exceptions are isolated with `asyncio.gather(..., return_exceptions=True)`.

## Emit Forms

Explicit tool name:

```python
await event_manager.emit("custom_event", "my_tool", {"value": 1})
```

Payload-only shorthand from inside a running event loop:

```python
event_manager.emit("custom_event", {"value": 1})
```

If the payload is a dict, `tool_name` is added when missing.

## Introspection

```python
from kavach_events import MCP_HOOKS, event_manager

event_manager.has_listeners(MCP_HOOKS.SECURITY_CHECK, "db_query")
event_manager.get_registered_hooks()
event_manager.get_registered_hooks(MCP_HOOKS.PRE_TOOL_CALL)
```

## With Kavach Shield

`KavachMiddleware` automatically emits:

- `pre_tool_call` for every tool call.
- `post_tool_call` after success.
- `security_check` when inbound or outbound scanning finds violations.
- `tool_error` when tool execution raises.

Manual `audit_log` events can be emitted from your application code.

