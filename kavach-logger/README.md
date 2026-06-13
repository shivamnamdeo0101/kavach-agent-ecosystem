# Kavach Logger

Zero-dependency logging helpers for Kavach packages and security-sensitive apps.

## Install

```bash
pip install kavach-logger
```

For local development:

```bash
pip install -e .
```

## What It Provides

- `DefaultLogger`: simple stderr logger.
- `MaskedLogger`: masks common secrets before logging.
- `get_logger(name="kavach", masked=True)`: create a logger instance.
- `mask_sensitive_data(text)`: mask a string manually.
- `BaseLogger`: interface for custom loggers.
- `LoggerManager` / `set_custom_logger`: optional singleton-style logger storage.

## Quick Use

```python
from kavach_logger import get_logger, mask_sensitive_data

logger = get_logger("api", masked=True)
logger.info("Using key sk-12345678901234567890")

plain = get_logger("debug", masked=False)
plain.info("This message is not modified")

safe_text = mask_sensitive_data("password: secret123")
```

## Masked Patterns

`MaskedLogger` currently masks:

- `AKIA...`, `sk-...`, and `api_key...` style values.
- Bearer/token values.
- 16-digit card-like numbers.
- `password`, `passwd`, `access_key`, and `secret` fields.

Masking is best-effort. Treat it as a safety layer, not a replacement for avoiding secrets in logs.

## Custom Logger

```python
from kavach_logger import DefaultLogger, LoggerManager, set_custom_logger

class AppLogger(DefaultLogger):
    def info(self, msg, **kwargs):
        super().info(f"[APP] {msg}", **kwargs)

set_custom_logger(AppLogger("app"))
logger = LoggerManager().get_logger()
logger.info("custom logger from manager")
```

Logger methods accept a message and optional keyword data:

```python
logger.info("security event", tool="db_query")
logger.warning("policy warning", rule="sql-injection")
logger.error("blocked request", user_id="u_123")
logger.debug("scanner details")
```
