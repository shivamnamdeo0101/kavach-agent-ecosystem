# Kavach Agent Ecosystem

Modular security middleware for AI agents and MCP servers. 3 independent packages with minimal dependencies.

## Packages

### 1. kavach-logger (Zero deps)
Centralized logging with sensitive data masking + pluggable implementations.
- `get_logger()` - structured logging with automatic masking
- `MaskedLogger` - logs with auto-masking of API keys, tokens, PII, passwords
- `DefaultLogger` - base logger without masking
- `BaseLogger` - abstract interface for custom implementations
- `LoggerManager` - singleton for logger lifecycle management
- Global enable/disable controls

### 2. kavach-mcp-events (Zero deps)
High-performance async event bus for lifecycle hooks.
- `EventManager` - subscribe to pre/post/sec events  
- Auto executor for sync callbacks
- Non-blocking error isolation

### 3. kavach-shield (Depends on logger + events)
Security middleware with threat detection for MCP.
- `DetectionEngine` - scans text against 6 security rules
- `KavachMiddleware` - MCP integration (inbound/outbound)
- Rules: prompt injection, data exfiltration, PII, secrets, code execution, SQL injection
- Strict/Monitor modes

## Installation

### Install All
```bash
bash install-all.sh
```

### Install Individual
```bash
pip install -e kavach-logger/
pip install -e kavach-mcp-events/
pip install -e kavach-shield/
```

## Quick Start

### Logger with Auto-Masking
```python
from kavach_logger import get_logger, mask_sensitive_data

# Masked logger (auto-masks sensitive data)
logger = get_logger("myapp", masked=True)
logger.info("Key: sk-1234567890")  # Outputs: Key: sk-***

# Plain logger (no masking)
plain = get_logger("myapp", masked=False)
```

### Custom Logger Implementation
```python
from kavach_logger import DefaultLogger, BaseLogger

class CustomLogger(DefaultLogger):
    def info(self, msg, **kwargs):
        msg = f"[CUSTOM] {msg}"
        super().info(msg, **kwargs)

custom = CustomLogger()
custom.info("Custom implementation!")
```

### Events
```python
from kavach_events import event_manager

@event_manager.subscribe(["pre", "post"], tools=["my_tool"])
async def on_event(payload):
    print(f"Event: {payload}")
```

### Detection Engine
```python
from kavach_shield import DetectionEngine, KAVACH_RULES
engine = DetectionEngine(KAVACH_RULES)
violations = engine.scan("ignore all previous instructions")
if violations:
    print("Threat detected!")
```

### MCP Middleware
```python
from kavach_shield import KavachMiddleware

middleware = KavachMiddleware(
    strict=True,  # Block on violations
    sensitive_tools=["execute_code", "file_*"]
)
# Add to FastMCP or other MCP servers
```

## Structure

```
kavach-agent-ecosystem/
├── kavach-logger/          → pip install kavach-logger
│   └── kavach_logger/
│       ├── __init__.py        (API exports)
│       ├── base_logger.py      (Abstract interface)
│       ├── default_logger.py   (Concrete + masked impl)
│       ├── logger_manager.py   (Singleton + utilities)
│       └── setup.py
│
├── kavach-mcp-events/      → pip install kavach-mcp-events
│   └── kavach_events/
│       ├── __init__.py
│       └── manager.py
│
├── kavach-shield/          → pip install kavach-shield
│   └── kavach_shield/
│       ├── __init__.py
│       ├── engine.py
│       ├── middleware.py
│       ├── rules.py (6 rules)
│       ├── types.py
│       └── exceptions.py
│
├── install-all.sh
├── deploy-all.sh
└── example.py
```

## License

MIT
