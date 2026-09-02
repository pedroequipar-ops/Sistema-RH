import json
import logging


class LoggerEngine:
    """Wrapper único de logging do sistema. Nunca usar print()."""

    def __init__(self, name="sistema_rh"):
        self._logger = logging.getLogger(name)

    def _log(self, level, message, context):
        if context:
            message = f"{message} | {json.dumps(context, default=str, ensure_ascii=False)}"
        self._logger.log(level, message)

    def debug(self, message, **context):
        self._log(logging.DEBUG, message, context)

    def info(self, message, **context):
        self._log(logging.INFO, message, context)

    def warning(self, message, **context):
        self._log(logging.WARNING, message, context)

    def error(self, message, **context):
        self._log(logging.ERROR, message, context)

    def exception(self, message, **context):
        if context:
            message = f"{message} | {json.dumps(context, default=str, ensure_ascii=False)}"
        self._logger.exception(message)

    def critical(self, message, **context):
        self._log(logging.CRITICAL, message, context)


logger = LoggerEngine()
