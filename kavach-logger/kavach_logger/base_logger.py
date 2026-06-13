class BaseLogger:
    def info(self, msg, **kwargs):
        raise NotImplementedError

    def error(self, msg, **kwargs):
        raise NotImplementedError

    def debug(self, msg, **kwargs):
        raise NotImplementedError

    def warning(self, msg, **kwargs):
        raise NotImplementedError
