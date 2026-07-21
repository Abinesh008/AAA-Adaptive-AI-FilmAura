import asyncio
from typing import Dict, List, Any, Callable, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger("app.retrieval.event_bus")

class RetrievalEvent(BaseModel):
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())

EventCallback = Callable[[RetrievalEvent], Awaitable[None]]

class RetrievalEventBus:
    """
    Decoupled event bus managing pub/sub listeners for all stages of retrieval.
    """
    def __init__(self):
        self._listeners: Dict[str, List[EventCallback]] = {}

    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        name = event_type.lower()
        if name not in self._listeners:
            self._listeners[name] = []
        self._listeners[name].append(callback)
        logger.info(f"Subscribed callback to retrieval event: {name}")

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        name = event_type.lower()
        event = RetrievalEvent(event_type=name, payload=payload)
        listeners = self._listeners.get(name, [])
        
        # Dispatch events to all registered async listeners concurrently
        if listeners:
            tasks = []
            for listener in listeners:
                tasks.append(self._safe_dispatch(listener, event))
            await asyncio.gather(*tasks)

    async def _safe_dispatch(self, listener: EventCallback, event: RetrievalEvent) -> None:
        try:
            await listener(event)
        except Exception as e:
            logger.error(f"Error handling event {event.event_type} in subscriber: {str(e)}")

# Singleton event bus instance
event_bus = RetrievalEventBus()
