import os

files = {
    "backend/app/core/logger.py": """
import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _log(self, level: int, event: str, **kwargs: Any):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
""",
    "backend/app/core/events.py": """
from typing import Callable, Dict, List, Any
import asyncio
from app.core.logger import get_logger

logger = get_logger(__name__)

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_type: str, handler: Callable[..., Any]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info("Subscribed to event", event_type=event_type)

    async def publish(self, event_type: str, **payload: Any):
        logger.info(event_type, **payload)
        if event_type in self.subscribers:
            handlers = self.subscribers[event_type]
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(**payload)
                    else:
                        handler(**payload)
                except Exception as e:
                    logger.error("Event handler failed", event_type=event_type, error=str(e))

event_bus = EventBus()
""",
    "backend/app/core/executor.py": """
from typing import Callable, Any, Awaitable
from fastapi import BackgroundTasks
from app.core.logger import get_logger

logger = get_logger(__name__)

class JobExecutor:
    def submit(self, job_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any):
        raise NotImplementedError

class LocalBackgroundExecutor(JobExecutor):
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def submit(self, job_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any):
        self.background_tasks.add_task(job_func, *args, **kwargs)
        logger.info("Job submitted to LocalBackgroundExecutor", job_func=job_func.__name__)
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
