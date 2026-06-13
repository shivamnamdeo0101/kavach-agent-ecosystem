# Kavach MCP Events

High-performance async event bus with lifecycle hooks for AI agent security middleware.

## Features

✅ **Async-First Architecture** - Non-blocking event processing  
✅ **Tool-Specific & Global Listeners** - Subscribe to specific tools or all events  
✅ **Pre/Post/Lifecycle Hooks** - React to security events at any stage  
✅ **Auto Executor** - Transparent sync/async callback handling  
✅ **Error Isolation** - Listener failures don't block other handlers  
✅ **Zero Dependencies** - No external requirements

## Installation

```bash
pip install kavach-mcp-events
```

## Quick Start

### Using Standardized MCP Hooks (Recommended)

```python
from kavach_events import event_manager, MCP_HOOKS

# Subscribe to standardized MCP lifecycle events
@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL], tools=["execute_code"])
async def before_code_execution(payload):
    print(f"About to execute: {payload['arguments']}")

@event_manager.subscribe([MCP_HOOKS.POST_TOOL_CALL], tools=["execute_code"])
async def after_code_execution(payload):
    print(f"Execution result: {payload['response']}")

@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["*"])
async def on_threat(payload):
    print(f"⚠️  Threat detected: {len(payload['violations'])} violations")

# These events are auto-emitted by KavachMiddleware
# No manual emit() needed!
```

### Basic Event Subscription

```python
from kavach_events import event_manager

# Subscribe to custom events (manual control)
@event_manager.subscribe(["pre_execution", "post_execution"])
async def handle_event(payload):
    print(f"Event received: {payload}")

# Emit events manually
await event_manager.emit("pre_execution", "my_tool", {"data": "test"})
```

### Tool-Specific Listeners

```python
from kavach_events import event_manager, MCP_HOOKS

# Listen only to specific tools
@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["execute_code", "db_query"])
async def on_sensitive_tool(payload):
    print(f"Sensitive tool event: {payload}")

# Listen to all tools (wildcard)
@event_manager.subscribe([MCP_HOOKS.TOOL_ERROR], tools=["*"])
async def on_any_error(payload):
    print(f"Error on any tool: {payload}")
```

### Synchronous Callbacks

```python
from kavach_events import event_manager, MCP_HOOKS

# Sync callbacks are automatically executed in thread pool
@event_manager.subscribe([MCP_HOOKS.AUDIT_LOG])
def sync_handler(payload):  # No async needed
    with open("/var/log/security.log", "a") as f:
        f.write(str(payload))

await event_manager.emit(MCP_HOOKS.AUDIT_LOG, "db_query", {"query": "SELECT 1"})
```

### Check for Listeners

```python
from kavach_events import event_manager, MCP_HOOKS

# Check if any listeners exist before expensive operations
if event_manager.has_listeners(MCP_HOOKS.SECURITY_CHECK, "execute_code"):
    await event_manager.emit(MCP_HOOKS.SECURITY_CHECK, "execute_code", payload)
```

## API Reference

### `EventManager()`

Core event bus.

#### `subscribe(events: List[str], tools: Optional[List[str]] = None) -> Callable`

Decorator to register event listeners.

**Parameters:**
- `events` (List[str]): Event types to listen for (use `MCP_HOOKS.*` constants)
- `tools` (List[str]): Tool names to listen to. Defaults to ["*"] (all tools)

**Returns:** Decorator function

**Examples:**
```python
from kavach_events import MCP_HOOKS

# Listen to events on specific tools
@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL, MCP_HOOKS.POST_TOOL_CALL], tools=["file_write", "db_query"])

# Listen to all tools
@event_manager.subscribe([MCP_HOOKS.TOOL_ERROR], tools=["*"])

# Shorthand: listen to all tools
@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK])  # tools defaults to ["*"]
```

#### `emit(event_type: str, tool_name: str, data: Any) -> Coroutine`

Emit an event to all registered listeners.

**Parameters:**
- `event_type` (str): Type of event (use `MCP_HOOKS.*` constants)
- `tool_name` (str): Tool that triggered the event
- `data` (Any): Payload data for listeners

**Behavior:**
- Calls tool-specific listeners first
- Then calls global ("*") listeners
- Async callbacks run concurrently
- Sync callbacks run in thread pool
- Exceptions don't block other listeners

**Example:**
```python
from kavach_events import MCP_HOOKS

await event_manager.emit(
    MCP_HOOKS.SECURITY_CHECK,
    "execute_code",
    {"code": "print('hello')", "language": "python"}
)
```

#### `has_listeners(event_type: str, tool_name: str) -> bool`

Check if listeners exist for an event.

**Parameters:**
- `event_type` (str): Event type to check (use `MCP_HOOKS.*` constants)
- `tool_name` (str): Tool name to check

**Returns:** True if either tool-specific or global listeners exist

**Example:**
```python
from kavach_events import MCP_HOOKS

if event_manager.has_listeners(MCP_HOOKS.SECURITY_CHECK, "db_query"):
    # Skip expensive validation if no listeners
    await event_manager.emit(MCP_HOOKS.SECURITY_CHECK, "db_query", payload)
```

### Global Instance

```python
from kavach_events import event_manager

# Pre-instantiated singleton
await event_manager.emit(...)
```

## Standardized MCP Hooks

Use `MCP_HOOKS` constants for production-grade event handling:

```python
from kavach_events import MCP_HOOKS

# Standardized lifecycle hooks (auto-emitted by KavachMiddleware for ALL tools)
print(MCP_HOOKS.PRE_TOOL_CALL)      # "pre_tool_call"   - Before tool execution
print(MCP_HOOKS.POST_TOOL_CALL)     # "post_tool_call"  - After tool success
print(MCP_HOOKS.SECURITY_CHECK)     # "security_check"  - Threat detected
print(MCP_HOOKS.TOOL_ERROR)         # "tool_error"      - Tool execution failed
print(MCP_HOOKS.AUDIT_LOG)          # "audit_log"       - Audit trail events
```

### Auto-Emit: MCP Middleware Integration

**KavachMiddleware automatically emits standardized hooks for EVERY tool call:**

```python
from fastmcp import FastMCP
from kavach_shield import KavachMiddleware
from kavach_events import event_manager, MCP_HOOKS

mcp = FastMCP()

# Subscribe to auto-emitted events
@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL], tools=["*"])
async def on_every_tool_pre(payload):
    print(f"Tool: {payload['tool_name']}")

@event_manager.subscribe([MCP_HOOKS.POST_TOOL_CALL], tools=["*"])
async def on_every_tool_post(payload):
    print(f"Tool completed: {payload['tool_name']}")

# Add middleware (auto-emits all events)
mcp.add_middleware(KavachMiddleware(strict=True))

# No manual emit() needed - middleware handles it!
```

## Auto-Emit Behavior

**KavachMiddleware automatically emits these standardized events:**

| Event | Auto-Emit | Use Case |
|-------|-----------|----------|
| `pre_tool_call` | ✅ All tools | Before execution |
| `post_tool_call` | ✅ All tools | After success |
| `security_check` | ⚠️ Violations only | Threat detected |
| `tool_error` | ✅ On failure | Execution error |
| `audit_log` | Manual | Custom audit events |

## Examples

### Security Event Pipeline

```python
from kavach_events import event_manager, MCP_HOOKS

# Pre-execution validation (auto-emitted by middleware)
@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL], tools=["execute_code"])
async def validate_before_exec(payload):
    print(f"Validating code...")
    # Perform security checks

# Post-execution audit (auto-emitted by middleware)
@event_manager.subscribe([MCP_HOOKS.POST_TOOL_CALL], tools=["execute_code"])
async def audit_after_exec(payload):
    print(f"Audit: code executed successfully")
    # Log execution

# No manual emit() needed - middleware handles it!
```

### Error Handling with Global Listeners

```python
from kavach_events import event_manager, MCP_HOOKS

# Catch all errors (auto-emitted by middleware)
@event_manager.subscribe([MCP_HOOKS.TOOL_ERROR], tools=["*"])
async def global_error_handler(payload):
    print(f"Caught error on any tool: {payload}")
    # Send alert, log to monitoring system

# Tool-specific error handling
@event_manager.subscribe([MCP_HOOKS.TOOL_ERROR], tools=["db_query"])
async def db_error_handler(payload):
    print(f"Database error (with retry logic): {payload}")
    # Retry or fallback
```

### Async Event Batching

```python
from kavach_events import event_manager
import asyncio

# Multiple listeners, all run concurrently
@event_manager.subscribe(["batch_process"])
async def listener1(data):
    await asyncio.sleep(1)
    print("Listener 1 done")

@event_manager.subscribe(["batch_process"])
async def listener2(data):
    await asyncio.sleep(1)
    print("Listener 2 done")

# Both run in parallel (total ~1s, not ~2s)
await event_manager.emit("batch_process", "tool", {})
```

### Conditional Event Emission

```python
from kavach_events import event_manager, MCP_HOOKS

# Only emit if listeners exist (performance optimization)
if event_manager.has_listeners(MCP_HOOKS.SECURITY_CHECK, "my_tool"):
    # Expensive operation
    data = await fetch_detailed_metrics()
    await event_manager.emit(MCP_HOOKS.SECURITY_CHECK, "my_tool", data)
else:
    # Skip expensive operation if no listeners
    pass
```

## Performance Characteristics

- **Event Emission**: < 100μs overhead
- **Listener Registration**: O(1) per subscription
- **Max Concurrent Handlers**: Limited by asyncio event loop
- **Memory**: ~1KB per listener + payload size

## Use Cases

- **Security Event Auditing** - Track all security checks and violations
- **Tool Execution Hooks** - Pre/post processing for any tool
- **Distributed Tracing** - Emit events for observability
- **Reactive Programming** - React to security events in real-time
- **Testing & Monitoring** - Verify security pipeline execution

## Integration with Kavach Shield

```python
from kavach_shield import KavachMiddleware
from kavach_events import event_manager, MCP_HOOKS

# Listen to security violations from Shield
@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["*"])
async def on_threat(payload):
    print(f"Threat detected: {len(payload.get('violations', []))} violations")

# Create middleware (emits events automatically)
middleware = KavachMiddleware(rules=KAVACH_RULES)

# No manual emit() needed - middleware auto-emits all events!
```

## License

MIT License
