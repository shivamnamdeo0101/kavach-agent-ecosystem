# Kavach Logger

Centralized logging with automatic sensitive data masking for security-critical applications.

## Features

✅ **Automatic Data Masking** - Detects and redacts API keys, tokens, PII, passwords, and other sensitive information  
✅ **Pluggable Implementations** - Switch between masked/plain loggers or implement custom backends  
✅ **Structured Logging** - JSON-compatible log output with **kwargs support  
✅ **Singleton Logger Manager** - Unified logger lifecycle management  
✅ **Zero Dependencies** - No external requirements

## Installation

```bash
pip install kavach-logger
```

## Quick Start

### Basic Usage - Auto-Masking

```python
from kavach_logger import get_logger

# Creates a masked logger (auto-masks sensitive data)
logger = get_logger("myapp")
logger.info("API Key: sk-1234567890")  
# Output: API Key: sk-***
logger.error("Password: secret123")     
# Output: Password: ***
```

### Plain Logger (No Masking)

```python
from kavach_logger import get_logger

logger = get_logger("myapp", masked=False)
logger.info("Debug: token=abc123")  
# Output: Debug: token=abc123 (unmodified)
```

### Manual Data Masking

```python
from kavach_logger import mask_sensitive_data

data = "credit_card=4532123456789012"
masked = mask_sensitive_data(data)
print(masked)  # credit_card=****
```

### Custom Logger Implementation

```python
from kavach_logger import BaseLogger, DefaultLogger

class CustomLogger(DefaultLogger):
    def info(self, msg, **kwargs):
        msg = f"[CUSTOM] {msg}"
        super().info(msg, **kwargs)

custom = CustomLogger()
custom.info("Custom implementation!")  
# Output: [CUSTOM] Custom implementation!
```

### Logger Manager (Singleton)

```python
from kavach_logger import LoggerManager

# Get or create logger
logger1 = LoggerManager.get_logger("app", masked=True)
logger2 = LoggerManager.get_logger("app")  # Returns same instance

# Control all loggers
LoggerManager.enable_all()
LoggerManager.disable_all()
LoggerManager.enable_masking()  # Enable masking globally
LoggerManager.disable_masking()  # Disable masking globally
```

## API Reference

### `get_logger(name: str, masked: bool = True) -> BaseLogger`
Creates or retrieves a logger instance.

**Parameters:**
- `name` (str): Logger identifier
- `masked` (bool): Enable automatic masking (default: True)

**Returns:** `BaseLogger` instance

### `mask_sensitive_data(text: str) -> str`
Manually masks sensitive patterns in text.

**Patterns Masked:**
- API keys (sk-*, pk-*)
- Bearer tokens
- AWS credentials
- Passwords
- Credit card numbers
- Social security numbers
- Email addresses (partial)

### Logger Methods

```python
logger.info(msg, **kwargs)      # Info level
logger.error(msg, **kwargs)     # Error level
logger.debug(msg, **kwargs)     # Debug level
logger.warning(msg, **kwargs)   # Warning level
```

## Configuration

### Global Masking Control

```python
from kavach_logger import LoggerManager

# Disable masking for all loggers
LoggerManager.disable_masking()

# Re-enable masking
LoggerManager.enable_masking()
```

## Examples

### Logging with Structured Data

```python
logger = get_logger("security")

logger.info(
    "Security event detected",
    event_type="login",
    user_id="user123",
    token="sk-abc123xyz"
)
# Automatically masks the token
```

### Processing Sensitive Logs

```python
from kavach_logger import mask_sensitive_data

logs = [
    "User created with password: MyPass123!",
    "API call to https://api.example.com?token=abc123"
]

for log in logs:
    safe_log = mask_sensitive_data(log)
    print(safe_log)  # Safe to output/store
```

## Use Cases

- **Security Auditing** - Track security events without exposing credentials
- **PCI/HIPAA Compliance** - Automatic redaction for sensitive logs
- **Agent Logging** - Mask AI-generated content containing API keys/tokens
- **Production Debugging** - Safe log output in production environments

## License

MIT License
