from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from ..db import SessionLocal
import json
import logging
from .leaderboard import get_leaderboard

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Stream"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        msg_str = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(msg_str)
            except Exception as e:
                logger.error(f"Failed to send to websocket: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# Background task logic to trigger broadcast after a DB update
async def broadcast_leaderboard_update():
    db = SessionLocal()
    try:
        data = get_leaderboard(db)
        await manager.broadcast({
            "type": "LEADERBOARD_UPDATE",
            "data": data
        })
    finally:
        db.close()

async def broadcast_heat_update(event_id: str, timestamp: str, data: dict):
    # Sends a HEAT_UPDATE frame to build the timeline scrubber
    await manager.broadcast({
        "type": "HEAT_UPDATE",
        "scope": "event",
        "event_id": event_id,
        "timestamp": timestamp,
        "data": data
    })


@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial payload
        db = SessionLocal()
        initial_data = get_leaderboard(db)
        db.close()

        await websocket.send_text(json.dumps({
            "type": "LEADERBOARD_UPDATE",
            "data": initial_data
        }))

        while True:
            # Keep connection open.
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
