import json
import logging
from datetime import UTC, datetime
from typing import Any


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _log(self, level: int, event: str, **kwargs: Any):
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            **kwargs
        }
        self.logger.log(level, json.dumps(log_entry))

    def info(self, event: str, **kwargs: Any):
        self._log(logging.INFO, event, **kwargs)

    def error(self, event: str, **kwargs: Any):
        self._log(logging.ERROR, event, **kwargs)

    def warning(self, event: str, **kwargs: Any):
        self._log(logging.WARNING, event, **kwargs)

    def debug(self, event: str, **kwargs: Any):
        self._log(logging.DEBUG, event, **kwargs)

def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)
