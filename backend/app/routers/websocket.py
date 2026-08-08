"""WebSocket real-time telemetry and streaming router."""

import logging
from typing import Optional
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.utils.websocket_manager import manager
from app.utils.auth_utils import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket, token: Optional[str] = Query(None)):
    if not token:
        await websocket.close(code=4003)
        return

    payload = decode_access_token(token)
    if not payload or "user" not in payload:
        await websocket.close(code=4003)
        return

    await manager.connect("telemetry", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("telemetry", websocket)
    except Exception as e:
        logger.warning(f"WebSocket error on /ws/telemetry: {e}")
        manager.disconnect("telemetry", websocket)


@router.websocket("/ws/geolocation")
async def websocket_geolocation(websocket: WebSocket, token: Optional[str] = Query(None)):
    if not token:
        await websocket.close(code=4003)
        return

    payload = decode_access_token(token)
    if not payload or "user" not in payload:
        await websocket.close(code=4003)
        return

    await manager.connect("geolocation", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("geolocation", websocket)
    except Exception as e:
        logger.warning(f"WebSocket error on /ws/geolocation: {e}")
        manager.disconnect("geolocation", websocket)


@router.websocket("/ws/simulation")
async def websocket_simulation(websocket: WebSocket, token: Optional[str] = Query(None)):
    if not token:
        await websocket.close(code=4003)
        return

    payload = decode_access_token(token)
    if not payload or "user" not in payload:
        await websocket.close(code=4003)
        return

    await manager.connect("simulation", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("simulation", websocket)
    except Exception as e:
        logger.warning(f"WebSocket error on /ws/simulation: {e}")
        manager.disconnect("simulation", websocket)
