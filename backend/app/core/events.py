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
