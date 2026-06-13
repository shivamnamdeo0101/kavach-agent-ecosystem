import logging
import re

_logging_enabled = True
_masking_enabled = True

class LoggingFilter(logging.Filter):
    def filter(self, record):
        return _logging_enabled

def enable_logging(enabled: bool = True):
    global _logging_enabled
    _logging_enabled = enabled

def enable_masking(enabled: bool = True):
    global _masking_enabled
    _masking_enabled = enabled

def is_logging_enabled() -> bool:
    return _logging_enabled

def is_masking_enabled() -> bool:
    return _masking_enabled

def mask_sensitive_data(text: str) -> str:
    if not _masking_enabled or not isinstance(text, str):
        return text
    text = re.sub(r'(AKIA|sk-|api[_-]?key)[^\s]{10,}', r'\1***', text, flags=re.I)
    text = re.sub(r'(bearer|token)[=:\s]+[^\s]{10,}', r'\1 ***', text, flags=re.I)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****', text)
    text = re.sub(r'(password|passwd)[=:\s]+[^\s,}]+', r'\1=***', text, flags=re.I)
    text = re.sub(r'(access_key|secret)[=:\s]+[^\s,}]+', r'\1=***', text, flags=re.I)
    return text

def get_logger(name: str = "kavach") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        handler = logging.StreamHandler()
        handler.addFilter(LoggingFilter())
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s | %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
