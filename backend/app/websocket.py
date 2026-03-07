import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# draft_id -> set of connected websockets
_connections: dict[int, set[WebSocket]] = defaultdict(set)
_broadcast_queue: asyncio.Queue | None = None


async def websocket_endpoint(websocket: WebSocket, draft_id: int):
    """Handle WebSocket connections for real-time draft updates."""
    await websocket.accept()
    _connections[draft_id].add(websocket)
    logger.info("WebSocket connected for draft %d (total: %d)", draft_id, len(_connections[draft_id]))

    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            # Client can send ping/pong or other messages
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        _connections[draft_id].discard(websocket)
        logger.info("WebSocket disconnected for draft %d", draft_id)


def broadcast_draft_update(draft_id: int, data: dict):
    """Broadcast an update to all connected clients for a draft.

    This is safe to call from sync code — it schedules the broadcast
    on the running event loop.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_async_broadcast(draft_id, data))
    except RuntimeError:
        logger.warning("No running event loop — skipping WebSocket broadcast")


async def _async_broadcast(draft_id: int, data: dict):
    """Send data to all WebSocket clients connected to a draft."""
    message = json.dumps(data)
    dead = set()
    for ws in _connections[draft_id]:
        try:
            await ws.send_text(message)
        except Exception:
            dead.add(ws)
    _connections[draft_id] -= dead
