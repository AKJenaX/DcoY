"""Live event store for real-time data ingestion."""

from typing import Any, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# In-memory event buffer (last 100 events)
live_events: List[Dict[str, Any]] = []
MAX_EVENTS = 100


def add_event(event: Dict[str, Any]) -> int:
    """
    Add an event to the live store.
    
    Args:
        event: Dictionary containing event data
        
    Returns:
        Current count of events in store
    """
    global live_events
    
    # Add timestamp if not present
    if "timestamp" not in event:
        event["timestamp"] = datetime.now().isoformat()
    
    live_events.append(event)
    logger.debug(f"Event added. Total: {len(live_events)}")
    
    # Keep only last MAX_EVENTS
    if len(live_events) > MAX_EVENTS:
        removed = live_events.pop(0)
        logger.debug(f"Removed oldest event. Current total: {len(live_events)}")
    
    return len(live_events)


def get_events() -> List[Dict[str, Any]]:
    """
    Get all events from the live store.
    
    Returns:
        List of all events (copy to prevent external modification)
    """
    return live_events.copy()


def clear_events() -> None:
    """Clear all events from the live store."""
    global live_events
    live_events = []
    logger.info("Live event store cleared")


def get_event_count() -> int:
    """Get current count of events in store."""
    return len(live_events)


def has_events() -> bool:
    """Check if there are any events in the store."""
    return len(live_events) > 0
