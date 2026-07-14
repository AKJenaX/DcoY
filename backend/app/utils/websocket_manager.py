import logging
import asyncio
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps channel name (str) to a set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "telemetry": set(),
            "geolocation": set(),
            "simulation": set(),
        }
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None

    async def connect(self, channel: str, websocket: WebSocket):
        if self.main_loop is None:
            try:
                self.main_loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
        
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"Client connected to WebSocket channel '{channel}'. Active count: {len(self.active_connections[channel])}")

    def disconnect(self, channel: str, websocket: WebSocket):
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)
            logger.info(f"Client disconnected from WebSocket channel '{channel}'. Active count: {len(self.active_connections[channel])}")

    async def broadcast(self, channel: str, message: Any):
        if channel not in self.active_connections or not self.active_connections[channel]:
            return
        
        dead_connections = set()
        # Create a copy of the set to iterate safely to avoid concurrent modification issues
        for websocket in list(self.active_connections[channel]):
            try:
                if isinstance(message, dict) or isinstance(message, list):
                    await websocket.send_json(message)
                else:
                    await websocket.send_text(str(message))
            except Exception as e:
                logger.warning(f"Error broadcasting to a connection on channel '{channel}': {e}")
                dead_connections.add(websocket)

        for dead_ws in dead_connections:
            self.disconnect(channel, dead_ws)


# Global manager instance
manager = ConnectionManager()


def broadcast_sync(channel: str, message: Any):
    """Synchronous wrapper to broadcast messages to WebSocket subscribers from background tasks/threads."""
    loop = manager.main_loop
    if loop is not None and loop.is_running():
        asyncio.run_coroutine_threadsafe(manager.broadcast(channel, message), loop)
    else:
        # Fallback if no loop has been captured yet or it is not running
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(manager.broadcast(channel, message), loop)
            else:
                loop.run_until_complete(manager.broadcast(channel, message))
        except Exception as e:
            logger.warning(f"Failed to broadcast synchronously to channel '{channel}': {e}")
