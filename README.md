# Kavach Agent Ecosystem

Modular security middleware for AI agents and MCP servers. 3 independent packages with minimal dependencies.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-kavach--agent--ecosystem.web.app-32d7df?style=for-the-badge&logo=firebase&logoColor=white)](https://kavach-agent-ecosystem.web.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Shivam%20Namdeo-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/shivamnamdeo0101/)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-7ddf9b?style=for-the-badge&logo=github&logoColor=0b1220)](#contributions-welcome)
[![License MIT](https://img.shields.io/badge/License-MIT-f4be68?style=for-the-badge)](#license)

## Live Website

🚀 **Explore Kavach Agent Ecosystem:** [https://kavach-agent-ecosystem.web.app/](https://kavach-agent-ecosystem.web.app/)

## Author

Built by **[Shivam Namdeo](https://www.linkedin.com/in/shivamnamdeo0101/)**.

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
- `EventManager` - subscribe to standardized MCP lifecycle events
- `MCP_HOOKS` - 5 standardized event types (PRE_TOOL_CALL, POST_TOOL_CALL, SECURITY_CHECK, TOOL_ERROR, AUDIT_LOG)
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
from kavach_events import event_manager, MCP_HOOKS

@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL, MCP_HOOKS.POST_TOOL_CALL], tools=["my_tool"])
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

## Contributions Welcome

[![Issues](https://img.shields.io/badge/Open-Issues-ff6b8a?style=for-the-badge&logo=github)](../../issues)
[![Pull Requests](https://img.shields.io/badge/Send-Pull%20Requests-32d7df?style=for-the-badge&logo=git&logoColor=white)](../../pulls)
[![Ideas](https://img.shields.io/badge/Share-Ideas-7ddf9b?style=for-the-badge&logo=githubdiscussions&logoColor=0b1220)](../../discussions)

Contributions are welcome. If you want to improve rules, add integrations, enhance docs, or propose new Kavach packages, feel free to open an issue or pull request.

## License

MIT
