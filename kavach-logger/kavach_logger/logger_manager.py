from .base_logger import BaseLogger
from .default_logger import DefaultLogger, MaskedLogger

class LoggerManager:
    _instance = None
    _logger: BaseLogger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    def set_logger(self, logger: BaseLogger):
        self._logger = logger

    def get_logger(self, masked: bool = True):
        if self._logger is None:
            self._logger = MaskedLogger() if masked else DefaultLogger()
        return self._logger

_manager = LoggerManager()

def get_logger(name: str = "kavach", masked: bool = True) -> BaseLogger:
    """Get logger instance. Use masked=True for automatic sensitive data masking."""
    logger = MaskedLogger(name) if masked else DefaultLogger(name)
    return logger

def set_custom_logger(logger: BaseLogger):
    """Override default logger with custom implementation."""
    _manager.set_logger(logger)

def mask_sensitive_data(text: str) -> str:
    """Utility to mask sensitive data."""
    logger = MaskedLogger()
    return logger._mask_sensitive(text)

    def info(self, msg, **kwargs):
        msg = self._mask_sensitive(str(msg))
        super().info(msg, **kwargs)

    def error(self, msg, **kwargs):
        msg = self._mask_sensitive(str(msg))
        super().error(msg, **kwargs)

    def debug(self, msg, **kwargs):
        msg = self._mask_sensitive(str(msg))
        super().debug(msg, **kwargs)

    def warning(self, msg, **kwargs):
        msg = self._mask_sensitive(str(msg))
        super().warning(msg, **kwargs)
