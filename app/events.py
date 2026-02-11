"""Internal asyncio pub/sub event bus for CyberDemo.

The orchestrator publishes events here alongside its SSE yields.
The Director agent subscribes to receive events in real time.
Uses asyncio.Queue for zero-latency internal communication.
"""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Active subscriber queues — each Director SSE connection gets one
_subscribers: list[asyncio.Queue] = []


def subscribe() -> asyncio.Queue:
    """Create a new subscriber queue. Returns a Queue that receives events."""
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.append(q)
    logger.info(f"Event bus: new subscriber (total: {len(_subscribers)})")
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    """Remove a subscriber queue."""
    if q in _subscribers:
        _subscribers.remove(q)
        logger.info(f"Event bus: subscriber removed (total: {len(_subscribers)})")


async def publish(event: dict[str, Any]) -> None:
    """Publish an event to all subscribers. Non-blocking — drops if queue is full."""
    for q in _subscribers:
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("Event bus: subscriber queue full, dropping event")
