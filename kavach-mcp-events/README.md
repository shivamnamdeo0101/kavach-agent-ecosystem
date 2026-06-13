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

### Basic Event Subscription

```python
from kavach_events import event_manager

# Subscribe to specific events
@event_manager.subscribe(["pre_execution", "post_execution"])
async def handle_event(payload):
    print(f"Event received: {payload}")

# Emit events
await event_manager.emit("pre_execution", "my_tool", {"data": "test"})
```

### Tool-Specific Listeners

```python
from kavach_events import event_manager

# Listen only to specific tools
@event_manager.subscribe(["security_check"], tools=["execute_code", "db_query"])
async def on_sensitive_tool(payload):
    print(f"Sensitive tool event: {payload}")

# Listen to all tools (wildcard)
@event_manager.subscribe(["error"], tools=["*"])
async def on_any_error(payload):
    print(f"Error on any tool: {payload}")
```

### Synchronous Callbacks

```python
from kavach_events import event_manager

# Sync callbacks are automatically executed in thread pool
@event_manager.subscribe(["log_event"])
def sync_handler(payload):  # No async needed
    with open("/var/log/security.log", "a") as f:
        f.write(str(payload))

await event_manager.emit("log_event", "db_query", {"query": "SELECT 1"})
```

### Check for Listeners

```python
from kavach_events import event_manager

# Check if any listeners exist before expensive operations
if event_manager.has_listeners("security_check", "execute_code"):
    await event_manager.emit("security_check", "execute_code", payload)
```

## API Reference

### `EventManager()`

Core event bus.

#### `subscribe(events: List[str], tools: Optional[List[str]] = None) -> Callable`

Decorator to register event listeners.

**Parameters:**
- `events` (List[str]): Event types to listen for
- `tools` (List[str]): Tool names to listen to. Defaults to ["*"] (all tools)

**Returns:** Decorator function

**Examples:**
```python
# Listen to events on specific tools
@event_manager.subscribe(["pre", "post"], tools=["file_write", "db_query"])

# Listen to all tools
@event_manager.subscribe(["error"], tools=["*"])

# Shorthand: listen to all tools
@event_manager.subscribe(["security_event"])  # tools defaults to ["*"]
```

#### `emit(event_type: str, tool_name: str, data: Any) -> Coroutine`

Emit an event to all registered listeners.

**Parameters:**
- `event_type` (str): Type of event
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
await event_manager.emit(
    "security_check",
    "execute_code",
    {"code": "print('hello')", "language": "python"}
)
```

#### `has_listeners(event_type: str, tool_name: str) -> bool`

Check if listeners exist for an event.

**Parameters:**
- `event_type` (str): Event type to check
- `tool_name` (str): Tool name to check

**Returns:** True if either tool-specific or global listeners exist

**Example:**
```python
if event_manager.has_listeners("security_check", "db_query"):
    # Skip expensive validation if no listeners
    await event_manager.emit("security_check", "db_query", payload)
```

### Global Instance

```python
from kavach_events import event_manager

# Pre-instantiated singleton
await event_manager.emit(...)
```

## Common Event Types

| Event | Typical Use | Payload |
|-------|-------------|----------|
| `pre_execution` | Pre-flight checks | tool_input, tool_name |
| `post_execution` | Post-execution hooks | result, tool_name |
| `security_check` | Security validation | input_data, rule_set |
| `security_violation` | Threat detected | violation, severity |
| `error` | Error handling | error_msg, exception |
| `log_event` | Audit logging | message, metadata |

## Examples

### Security Event Pipeline

```python
from kavach_events import event_manager

# Pre-execution validation
@event_manager.subscribe(["pre_execution"], tools=["execute_code"])
async def validate_before_exec(payload):
    print(f"Validating code...")
    # Perform security checks

# Post-execution audit
@event_manager.subscribe(["post_execution"], tools=["execute_code"])
async def audit_after_exec(payload):
    print(f"Audit: code executed successfully")
    # Log execution

# Emit the pipeline
await event_manager.emit("pre_execution", "execute_code", {"code": "..."})
# ... code execution happens ...
await event_manager.emit("post_execution", "execute_code", {"result": "..."})
```

### Error Handling with Global Listeners

```python
from kavach_events import event_manager

# Catch all errors
@event_manager.subscribe(["error"], tools=["*"])
async def global_error_handler(payload):
    print(f"Caught error on any tool: {payload}")
    # Send alert, log to monitoring system

# Tool-specific error handling
@event_manager.subscribe(["error"], tools=["db_query"])
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
from kavach_events import event_manager

# Only emit if listeners exist (performance optimization)
if event_manager.has_listeners("expensive_event", "my_tool"):
    # Expensive operation
    data = await fetch_detailed_metrics()
    await event_manager.emit("expensive_event", "my_tool", data)
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
from kavach_events import event_manager

# Listen to security violations from Shield
@event_manager.subscribe(["security_violation"])
async def on_threat(payload):
    print(f"Threat: {payload['name']}")

# Create middleware (emits events automatically)
middleware = KavachMiddleware(rules=KAVACH_RULES)
```

## License

MIT License
