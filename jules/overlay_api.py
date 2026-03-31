import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .overlay_models import RivalryEvent, RHIContext
from .overlay_engine import OverlayEngine

app = FastAPI()
engine = OverlayEngine(max_overlays_per_window=2, cooldown_s=5)
active_connections = []

@app.websocket("/overlay/stream")
async def overlay_stream(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # In a real app, this consumes from NATS/Kafka.
            # We mock the ingestion by waiting for raw events over WS
            # OR simulating an internal loop.
            data = await websocket.receive_json()

            # Simple mock of parsing:
            try:
                event = RivalryEvent(**data.get("event", {}))
                context = RHIContext(**data.get("context", {}))

                # Evaluate candidates
                overlays = engine.evaluate(event, context)

                if overlays:
                    response = {
                        "type": "OVERLAY_RENDER",
                        "overlays": [o.dict() for o in overlays]
                    }
                    # Broadcast to all
                    for conn in active_connections:
                        await conn.send_json(response)

            except Exception as e:
                # Log parsing/eval errors quietly
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        active_connections.remove(websocket)
