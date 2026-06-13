import logging
import re
from .base_logger import BaseLogger

class DefaultLogger(BaseLogger):
    def __init__(self, name="kavach", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s] %(asctime)s | %(message)s", datefmt="%H:%M:%S")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg, **kwargs):
        if kwargs:
            msg = f"{msg} | {kwargs}"
        self.logger.info(msg)

    def error(self, msg, **kwargs):
        if kwargs:
            msg = f"{msg} | {kwargs}"
        self.logger.error(msg)

    def debug(self, msg, **kwargs):
        if kwargs:
            msg = f"{msg} | {kwargs}"
        self.logger.debug(msg)

    def warning(self, msg, **kwargs):
        if kwargs:
            msg = f"{msg} | {kwargs}"
        self.logger.warning(msg)

class MaskedLogger(DefaultLogger):
    def __init__(self, name="kavach", level=logging.INFO, enable_masking=True):
        super().__init__(name, level)
        self.enable_masking = enable_masking

    def _mask_sensitive(self, text: str) -> str:
        if not self.enable_masking or not isinstance(text, str):
            return text
        text = re.sub(r'(AKIA|sk-|api[_-]?key)[^\s]{10,}', r'\1***', text, flags=re.I)
        text = re.sub(r'(bearer|token)[=:\s]+[^\s]{10,}', r'\1 ***', text, flags=re.I)
        text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****', text)
        text = re.sub(r'(password|passwd)[=:\s]+[^\s,}]+', r'\1=***', text, flags=re.I)
        text = re.sub(r'(access_key|secret)[=:\s]+[^\s,}]+', r'\1=***', text, flags=re.I)
        return text

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
